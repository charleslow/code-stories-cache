# Explanations Draft

## Chapter 0: The Big Picture
The short answer is **yes** — picoclaw has built-in, first-class Telegram support. No sidecar process, no external bridge, no plugin installation. Telegram is one of over a dozen **channels** that picoclaw can connect to simultaneously.

The architecture revolves around a few key concepts. A **channel** is a platform adapter (Telegram, Discord, Slack, etc.) that translates platform-specific messages into a uniform internal format. The **MessageBus** is a set of buffered Go channels that decouple inbound messages (from users) from outbound messages (from the AI agent). The **Manager** orchestrates channel lifecycles, dispatches messages, handles rate limiting, and manages a pre-send pipeline for typing indicators and placeholder messages. Each channel implementation embeds a **BaseChannel** for shared logic like allowlists and group filtering, then adds platform-specific behavior.

The Telegram channel maintains a **persistent connection** via long polling — no public URL or webhook setup required. Let's trace exactly how this works, from registration to reply delivery.

## Chapter 1: Plugging In
Every channel in picoclaw registers itself through a factory pattern that eliminates hard-coded dependencies. In `init.go` (line 10), the Telegram package calls `channels.RegisterFactory("telegram", ...)`, passing a constructor that creates a `TelegramChannel`. This runs at program startup thanks to Go's `init()` mechanism — simply importing the package is enough.

The registry in `registry.go` is equally clean: a mutex-protected map of `string → ChannelFactory` functions (lines 14-17). `RegisterFactory` writes to it, `getFactory` reads from it. The Manager never imports `telegram` directly — it just looks up `"telegram"` in the map. This means adding a new channel requires zero changes to the Manager. The pattern scales: you can see in the codebase that Discord, Slack, WhatsApp, and many others each have their own `init.go` doing the exact same thing.

## Chapter 2: Configuration
`TelegramConfig` (lines 237-246) is a compact struct with environment variable overrides for every field — notice the `env:` tags. The `Token` is the BotFather-issued API token, `Proxy` supports SOCKS5/HTTP proxies for restricted networks, and `AllowFrom` is a `FlexibleStringSlice` that accepts both string and numeric user IDs.

The example config (lines 49-57) shows the minimal setup: set `enabled` to `true`, paste your bot token, and add your Telegram user ID to `allow_from`. That's it — three fields to get a working Telegram bot.

## Chapter 3: Building the Bot
`NewTelegramChannel` (line 52) takes the global `Config` and a `MessageBus`, then constructs the full Telegram channel in three steps. First, lines 56-73 handle proxy configuration with a nice fallback chain: explicit config proxy → environment variables → no proxy. Second, line 75 creates the `telego.Bot` instance with the token and any proxy options. Third, lines 80-88 construct a `BaseChannel` using the functional options pattern — `WithMaxMessageLength(4096)` tells the Manager to auto-split long messages at Telegram's limit, `WithGroupTrigger` wires up group chat filtering, and `WithReasoningChannelID` optionally routes chain-of-thought to a separate chat.

The struct itself (lines 41-50) reveals the composition: `*channels.BaseChannel` is embedded for shared behavior, while `bot`, `bh` (BotHandler), `commands`, and `chatIDs` are Telegram-specific. The `ctx` and `cancel` fields manage the channel's lifecycle context — a pattern we'll see used in `Start()`.

## Chapter 4: Long Polling
`Start()` is where the persistent connection to Telegram is established. Line 110 is the key call: `bot.UpdatesViaLongPolling(ctx, &telego.GetUpdatesParams{Timeout: 30})`. This opens an HTTP connection to Telegram's servers that blocks for up to 30 seconds waiting for new messages. When one arrives (or the timeout expires), it returns immediately and reconnects. The 30-second timeout is Telegram's maximum — it minimizes HTTP overhead while keeping latency under a second for new messages.

Why long polling instead of webhooks? Picoclaw is designed as a *personal* AI agent, often running on a laptop, Raspberry Pi, or behind NAT. Webhooks require a publicly reachable URL with TLS — a significant setup burden. Long polling just works, anywhere, with no firewall configuration.

Lines 125-142 register message handlers on the `BotHandler`: specific commands (`/start`, `/help`, `/show`, `/list`) get their own handlers, and `th.AnyMessage()` catches everything else and routes it to `handleMessage`. Line 149 launches the handler in a goroutine — the `Start()` method returns immediately so the Manager can start other channels concurrently.

## Chapter 5: Receiving Messages
When a Telegram message arrives, `handleMessage` transforms it from Telegram's world into picoclaw's uniform format. Lines 415-422 construct a `SenderInfo` with the canonical ID format `"telegram:<user_id>"`, giving every user a cross-platform identity. Line 425 checks the allowlist *before* doing any expensive work like downloading attachments — a smart optimization that avoids wasting bandwidth on rejected users.

Lines 432-454 are where the message content is assembled. The `chatIDs` map (line 433) caches the mapping from user ID to chat ID for future outbound messages. The `storeMedia` closure (lines 443-454) is a clever local helper that registers downloaded files with picoclaw's media store, falling back to raw file paths if the store isn't available. Lines 456-465 extract the text and caption, while subsequent code (not shown here) handles photos, voice messages, audio, and documents the same way.

## Chapter 6: Group Triggers
In group chats, you don't want the bot responding to every message. Lines 518-528 show how picoclaw handles this: first it checks whether the bot was `@mentioned` (line 519), strips the mention from the content (line 521), then delegates the decision to `ShouldRespondInGroup` (line 523). If the method returns `false`, the handler silently drops the message.

`ShouldRespondInGroup` in `base.go` (lines 132-158) implements a three-tier decision tree. If mentioned, always respond (line 137). If `mention_only` is configured, require mention (line 142). If prefix triggers are configured (like `!ask` or `/bot`), respond only when the message starts with a matching prefix and strip it (lines 148-149). With no group trigger config at all, the default is permissive — respond to everything. This logic lives in `BaseChannel` so every channel gets the same behavior for free.

## Chapter 7: The Bus
`MessageBus` (lines 16-22) is refreshingly simple: three buffered Go channels — `inbound`, `outbound`, and `outboundMedia` — plus a `done` channel for shutdown signaling and an atomic `closed` flag.

`PublishInbound` (lines 33-48) shows the publish pattern used everywhere: check if closed, check context, then attempt a non-blocking send with a `select` that can also abort on shutdown or context cancellation. This design means a slow consumer never blocks the Telegram polling loop indefinitely — the buffer absorbs bursts, and context cancellation provides a clean escape hatch. The bus is the central nervous system: channels publish inbound, the agent consumes and processes, then publishes outbound, and the Manager dispatches back to channels.

## Chapter 8: Routing Replies
When the agent produces a reply, it lands on the outbound bus. The Manager's dispatcher routes it to the correct channel worker. `newChannelWorker` (lines 437-452) creates a per-channel worker with a dedicated queue and a **rate limiter** — Telegram gets 20 messages per second (line 61 in the rate config), while Discord and Slack get just 1 msg/s, reflecting each platform's API limits.

`runWorker` (lines 456-482) is the consumer loop. It reads messages from the queue, checks if the channel provides a `MaxMessageLength` (line 466), and if the message exceeds it, splits it using `SplitMessage` (line 469). For Telegram, this threshold is 4096 characters — set back in the constructor. Each chunk is sent via `sendWithRetry`, which handles the pre-send pipeline and exponential backoff.

## Chapter 9: Typing & Placeholders
Before actually delivering a reply, `preSend` (lines 118-148) executes a three-step cleanup pipeline. Step 1 (line 122): stop the typing indicator goroutine that was started when the inbound message arrived. Step 2 (line 129): undo any message reaction (like a "thinking" emoji). Step 3 (line 136): try to edit the placeholder message with the actual reply content. If the edit succeeds (line 139), `preSend` returns `true` and the caller skips the normal `Send` — the user sees the placeholder morph into the real response, avoiding a duplicate message. If editing fails, it falls through to a normal send.

This pipeline is channel-agnostic — it works identically for any channel that implements the right interfaces.

## Chapter 10: Delivering the Reply
`Send()` converts the agent's markdown response into Telegram's supported HTML subset. Line 232 calls `markdownToTelegramHTML`, which handles headings, bold, italic, strikethrough, links, lists, and code blocks with a careful placeholder-based approach that prevents code content from being double-escaped.

Lines 238-246 show a pragmatic fallback: if Telegram rejects the HTML (perhaps due to malformed markup), the method retries with `ParseMode: ""` — plain text. Better to deliver an ugly message than no message at all.

## Chapter 11: Staying Alive
`StartTyping` (lines 255-279) tackles a subtle UX problem: Telegram's typing indicator expires after about 5 seconds, but AI processing can take much longer. The solution is a background goroutine that sends `ChatAction(typing)` every 4 seconds (line 266). The returned `cancel` function stops the goroutine cleanly — and it's idempotent, so calling it multiple times is safe. This is important because the Manager's `preSend` will call it, but context cancellation or the TTL janitor might also trigger cleanup.

## Chapter 12: Photos & Files
`SendMedia` handles outbound media attachments — images, audio, video, and generic files. Lines 341-342 iterate over message parts, resolving each media reference through the store. The type switch at line 360 maps picoclaw's generic media types to Telegram-specific API calls: `SendPhoto` for images, `SendAudio` for audio, `SendVideo` for video, and `SendDocument` as the fallback for everything else. Each call uses `telego.InputFile{File: file}` to stream the file directly without loading it entirely into memory.

Between the store resolution and the type switch, lines 351-358 open the local file. The `file.Close()` at line 391 happens after the send, ensuring the file descriptor is released even on success. Error handling (lines 343-348, 352-358) logs failures but continues to the next part — a single failed attachment doesn't prevent the rest from being delivered.

## Chapter 13: Slash Commands
The `TelegramCommander` interface (lines 13-18) defines four bot commands: `Start`, `Help`, `Show`, and `List`. The constructor (lines 25-30) creates a `cmd` struct holding the bot and config — simple dependency injection without a framework.

`Start` (lines 56-65) is representative of the pattern: receive the message context, send a reply with `ReplyParameters` so Telegram threads it as a response, and return any error. The commands are intentionally lightweight — `/show model` reports the current AI model, `/list channels` shows enabled channels. They give users basic introspection without leaving Telegram.

## Chapter 14: Optional Powers
`interfaces.go` defines the capability system that makes picoclaw's channel architecture extensible without modification. `TypingCapable` (line 8) lets a channel show a typing indicator. `MessageEditor` (line 14) enables editing existing messages. `ReactionCapable` (line 21) supports adding emoji reactions. `PlaceholderCapable` (line 30) combines with `MessageEditor` to enable the "Thinking... → actual response" pattern.

The Manager discovers these capabilities at runtime via Go type assertions — `if tc, ok := ch.(TypingCapable)`. A channel only implements what it supports. Telegram implements all four, while simpler channels might implement none. This is a textbook application of the Interface Segregation Principle: no channel is forced to implement capabilities it doesn't need.

## Chapter 15: Wrapping Up
Picoclaw's Telegram integration is not a bolt-on or a sidecar — it's a native channel that plugs into a well-designed extensible architecture. The journey we traced covered the full lifecycle: factory self-registration eliminates coupling, configuration is minimal (three fields), long polling provides a persistent connection without requiring public URLs, and the MessageBus cleanly decouples the Telegram adapter from the AI agent.

Several design patterns stood out. The capability interface system lets each channel opt into features like typing indicators, placeholders, and media without a monolithic interface. The pre-send pipeline elegantly coordinates typing stops, reaction undos, and placeholder edits before each reply. Rate limiting and exponential backoff protect against Telegram API limits without manual tuning. And the markdown-to-HTML converter's placeholder technique keeps code blocks safe from double-escaping.

If you ever needed to build a Telegram sidecar instead, you'd essentially be reimplementing what's already here: a long-polling loop, a message translation layer, and a way to shuttle messages to/from the AI agent. But with picoclaw, you don't have to — just set `"enabled": true` and paste your bot token.

STAGE_5_COMPLETE
