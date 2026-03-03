# Explanations Draft

## Chapter 0: Overview (150-200 words)
**The short answer is yes** — picoclaw has full, native Telegram integration. There's no need to build a separate sidecar service. Telegram is one of roughly fifteen messaging **channels** that picoclaw supports as first-class citizens, alongside Discord, Slack, WhatsApp, Feishu, and others.

The architecture centers on a few key concepts. A **channel** is any messaging platform adapter — it knows how to receive and send messages using a specific platform's API. The **MessageBus** is an internal pub/sub system that decouples channels from the AI agent loop. The **Manager** orchestrates all active channels, handling rate limiting, retries, and per-channel worker queues. For Telegram specifically, the persistent connection uses **long polling** — the bot continuously asks Telegram's servers for new updates, making it work behind NAT without needing a public webhook URL. Finally, channels register themselves through a **plugin registry** pattern using Go's `init()` mechanism, so the core system never directly imports any specific channel.

Let's trace how Telegram plugs into this system, from registration to message flow.

## Chapter 1: Plugin Registry (~120 words)
`RegisterFactory` on line 20 accepts a name and a constructor function, storing them in a mutex-protected map. `getFactory` on line 27 retrieves them. This is the entire plugin system — just 23 lines of code.

The second snippet shows Telegram's side of the handshake. The `init()` function on line 9 runs automatically when the package is imported, calling `RegisterFactory("telegram", ...)` with a closure that constructs a `TelegramChannel`. The Manager never needs to know about the `telegram` package directly — it just calls `getFactory("telegram")` at startup.

This pattern is idiomatic Go: each channel self-registers in its own `init()`, and the system discovers available channels at runtime through the shared registry.

## Chapter 2: Factory Activation (~100 words)
The blank imports on lines 16–28 are the mechanism that activates the plugin registry. Each `_ "github.com/sipeed/picoclaw/pkg/channels/telegram"` import causes Go to execute that package's `init()` function, which registers the factory — but the gateway code never references the telegram package directly.

In the second snippet, `initChannels()` at line 209 checks if Telegram is both enabled and has a token configured before calling `m.initChannel("telegram", "Telegram")`, which looks up the factory and invokes it. This two-phase approach — register-then-activate — means disabled channels have zero runtime cost.

## Chapter 3: Telegram Config (~80 words)
`TelegramConfig` defines everything the Telegram channel needs to start. The `Token` (line 239) is the BotFather-issued API token — the only required field beyond `Enabled`. The optional `Proxy` (line 240) supports environments where Telegram's API is blocked. `AllowFrom` (line 241) restricts which user IDs can interact with the bot. `GroupTrigger`, `Typing`, and `Placeholder` control behavioral features we'll explore in later chapters.

## Chapter 4: Bot Construction (~180 words)
`TelegramChannel` on line 41 embeds `*channels.BaseChannel`, inheriting shared functionality like allowlist checking and message publishing. It adds Telegram-specific fields: the `telego.Bot` client, a `BotHandler` for routing updates, a `TelegramCommander` for slash commands, and a `chatIDs` map that tracks which chat each user belongs to.

The constructor `NewTelegramChannel` on line 52 builds this in three stages. First (lines 53–73), it configures HTTP proxy support — checking the config's `Proxy` field first, then falling back to `HTTP_PROXY`/`HTTPS_PROXY` environment variables. This is important because Telegram's API is blocked in some regions, so proxy support isn't an afterthought.

Second (line 75), the `telego.Bot` is created with the bot token and any configured options. Third (lines 80–96), a `BaseChannel` is composed with Telegram-specific settings: the 4096-character message limit (Telegram's API constraint), the group trigger configuration, and the reasoning channel ID. The result is a fully configured channel ready to start polling.

## Chapter 5: Long Polling — Persistent Connection (~220 words)
This is the answer to the "persistent connection" question. Line 110 calls `bot.UpdatesViaLongPolling` with a 30-second timeout — this establishes a long-lived HTTP connection to Telegram's servers that blocks until new updates arrive or the timeout elapses. When it times out, it immediately reconnects. This loop runs continuously, giving the bot near-real-time message delivery without needing a publicly accessible webhook URL.

Between the two snippets, lines 118–123 create a `BotHandler` that routes incoming updates. The command registrations on lines 125–142 are straightforward: `/start`, `/help`, `/show`, and `/list` get dedicated handlers, while line 142 registers a catch-all for any other message via `th.AnyMessage()`.

Line 144 marks the channel as running, and lines 149–155 launch the bot handler in a separate goroutine. The `Start` method returns immediately — the actual message processing happens asynchronously.

Why long polling instead of webhooks? PicoClaw is designed as a personal AI agent that runs on any machine — a laptop, a Raspberry Pi, a home server. Long polling works from behind NAT, firewalls, and dynamic IPs without needing port forwarding or a domain name. This design choice prioritizes ease of deployment over the marginal latency improvement webhooks would provide.

## Chapter 6: Channel Contract (~150 words)
The `Channel` interface on line 43 defines the minimum contract: `Name()`, `Start()`, `Stop()`, `Send()`, `IsRunning()`, plus access control methods. Every channel — Telegram, Discord, Slack — must implement these six methods.

`BaseChannel` on line 81 provides the shared implementation. Notice it's a struct, not an interface — channels embed it using Go's composition. The `running` field (line 84) uses `atomic.Bool` for lock-free concurrent access. The `allowList` (line 86) controls who can talk to the bot. The `owner` field (line 91) is a back-reference to the concrete channel that embeds this BaseChannel — it enables `HandleMessage` to discover optional capabilities like typing indicators through type assertions.

`NewBaseChannel` on line 95 accepts functional options (`BaseChannelOption`), which is why the Telegram constructor can pass `WithMaxMessageLength(4096)` and `WithGroupTrigger(...)` cleanly without a massive parameter list.

## Chapter 7: Capability Interfaces (~100 words)
These four interfaces define optional capabilities that channels can advertise. `TypingCapable` (line 8) enables "user is typing..." indicators. `MessageEditor` (line 14) allows editing sent messages. `PlaceholderCapable` (line 30) lets a channel send a temporary "Thinking..." message. `ReactionCapable` (line 21) adds emoji reactions to incoming messages.

Telegram implements `TypingCapable`, `MessageEditor`, and `PlaceholderCapable` — but not `ReactionCapable`. The Manager discovers these at runtime via type assertions, so channels opt in simply by implementing the interface. No registration, no flags — just implement the method and it works.

## Chapter 8: Inbound Pipeline (~200 words)
When a Telegram message arrives, `handleMessage` on line 405 is the first stop. Lines 406–413 guard against nil messages and nil senders — defensive checks because Telegram can deliver system messages without a `From` field.

Lines 415–422 build a `bus.SenderInfo` struct with the sender's platform ID, canonical ID (format `telegram:12345`), username, and display name. Line 425 checks the allowlist early — if the sender isn't permitted, the message is silently dropped *before* any expensive operations like media downloads.

The second snippet picks up after media processing (photos, voice, audio, documents have been downloaded and stored between lines 440–515). Lines 518–528 handle group chat behavior: the bot checks if it was `@mentioned`, strips the mention from the content, and calls `ShouldRespondInGroup()` to decide whether to respond based on the configured group trigger (mention-only mode or prefix matching).

Finally, lines 538–564 construct the `Peer` (direct vs group), build the metadata map, and call `c.HandleMessage()` — which auto-triggers typing, reactions, and placeholders before publishing the `InboundMessage` onto the bus.

## Chapter 9: Message Bus (~130 words)
`MessageBus` on line 16 is remarkably simple: three buffered Go channels (capacity 64 each) for inbound messages, outbound messages, and outbound media, plus a `done` channel and an atomic `closed` flag.

`PublishInbound` on line 33 follows a defensive pattern: check if closed, check if context is cancelled, then select between sending on the channel, the done signal, or context cancellation. This triple-select prevents goroutine leaks under any shutdown scenario.

`ConsumeInbound` on line 50 mirrors this pattern for the reading side. The agent loop calls this in a continuous loop, blocking until a message arrives from any channel.

The bus is the sole communication path between channels and the agent — neither side knows about the other. This makes testing trivial: inject a mock bus and verify messages flow correctly.

## Chapter 10: Outbound Dispatch (~150 words)
`newChannelWorker` on line 437 creates a per-channel worker with its own message queue (capacity 16) and a `rate.Limiter`. Line 439 looks up a channel-specific rate from `channelRateConfig` — Telegram gets 20 messages/second, while Discord and Slack get just 1. The burst (line 442) is half the rate, rounded up, preventing short bursts from triggering platform rate limits.

`dispatchOutbound` on line 590 is a thin wrapper around the generic `dispatchLoop` function. It subscribes to outbound messages from the bus, extracts the channel name, and enqueues the message into the appropriate worker's queue. The `select` on line 597 ensures that if the worker's queue is full, the dispatcher blocks rather than dropping messages — backpressure propagates naturally.

This worker-per-channel architecture means a slow Telegram API response won't block Discord messages from being sent. Each channel processes at its own pace.

## Chapter 11: Sending Messages (~100 words)
`Send` on line 222 checks if the channel is running (line 223), parses the chat ID (line 227), then converts the message content from markdown to Telegram's HTML format (line 232). Lines 235–236 construct the Telegram message with HTML parse mode.

The clever part is lines 238–246: if the HTML parse fails (perhaps due to unbalanced tags from the AI's response), the code falls back to plain text by clearing `ParseMode` and retrying. This two-tier approach means the bot never silently drops a message — the user always gets a response, even if formatting is lost.

## Chapter 12: Typing Indicator (~80 words)
`StartTyping` sends an immediate "typing" action on line 262, then spawns a goroutine that repeats it every 4 seconds via a ticker (line 266). Why 4 seconds? Telegram's typing indicator expires after roughly 5 seconds, so 4 gives reliable overlap without unnecessary API calls. The goroutine exits cleanly when the returned `cancel` function is called, which happens automatically when the Manager calls `preSend` before delivering the response.

## Chapter 13: Placeholder Edit (~180 words)
`SendPlaceholder` on line 301 checks if the placeholder feature is enabled in config (line 303). If so, it sends a "Thinking... 💭" message (configurable text, line 307) and returns its message ID. This ID gets stored by the Manager via `RecordPlaceholder`.

The second snippet shows the Manager's `preSend` method, which runs *before* every outbound message. It orchestrates three independent cleanup steps: line 122 stops the typing indicator, line 129 undoes any reaction, and line 136 tries to edit the placeholder.

The key insight is on lines 138–141: if the channel implements `MessageEditor` and the edit succeeds, `preSend` returns `true` — telling the caller to skip the normal `Send()`. The user sees their "Thinking..." message smoothly transform into the actual response, with no message deletion or duplication. If the edit fails (perhaps the placeholder was already deleted), execution falls through to a normal send.

This edit-in-place pattern creates a polished UX where the response appears to replace the thinking indicator seamlessly.

## Chapter 14: Bot Commands (~120 words)
`TelegramCommander` on line 13 defines the interface for bot slash commands: `/start`, `/help`, `/show`, and `/list`. The `cmd` struct on line 20 implements it, holding a reference to the bot and the global config.

The `Help` handler on line 40 is representative: it sends a message listing available commands, with the reply linked to the original command message via `ReplyParameters` on line 49. This threading makes it clear which command triggered which response.

`commandArgs` on line 32 is a simple utility that extracts everything after the command word — so `/show model` yields `"model"`. The commands themselves are lightweight introspection tools, letting users check the bot's current model and enabled channels directly from Telegram.

## Chapter 15: Media Handling (~170 words)
`SendMedia` on line 326 handles outbound media delivery. After the standard running check and chat ID parsing (lines 327–333), it resolves the media store on line 336. The media store is picoclaw's file lifecycle system — AI-generated images, audio, and documents are stored with references like `media://abc123` that any channel can resolve to a local file path.

Lines 341–342 iterate over `msg.Parts`, resolving each media reference to a local file. The `switch` on line 360 dispatches by media type: `SendPhoto` for images, `SendAudio` for audio, `SendVideo` for video, and `SendDocument` as the fallback for anything else. Each Telegram API call wraps the file in a `telego.InputFile` and includes an optional caption.

Between the two snippets (lines 341–358), each part is resolved from the media store and opened as a file handle. This indirection means the Telegram channel doesn't need to know *how* the file was created — it could be an AI-generated image, a downloaded attachment, or a user-uploaded document.

## Chapter 16: Summary (200 words)
PicoClaw doesn't just "support" Telegram — it treats Telegram as a first-class citizen in a multi-channel architecture. No sidecar needed.

The integration rests on several well-chosen design patterns. The **plugin registry** lets channels self-register via `init()`, keeping the core system decoupled from any specific platform. **Long polling** provides a persistent, always-on connection that works from behind NAT without needing public URLs — the bot is ready to receive messages the moment it starts. The **MessageBus** cleanly separates inbound and outbound flows, making the system testable and extensible.

On the UX side, the **placeholder edit pattern** gives users a smooth experience: a "Thinking..." message appears instantly and transforms into the actual response. The **typing indicator** with its 4-second refresh cycle provides real-time feedback. **Media handling** supports images, audio, video, and documents through a unified media store abstraction.

The capability interface system (TypingCapable, PlaceholderCapable, MessageEditor) is worth highlighting as an architectural takeaway: rather than requiring all channels to implement every feature, channels opt in by implementing specific interfaces, discovered at runtime through Go's type assertions. It's a clean way to handle the reality that every messaging platform is slightly different.

STAGE_5_COMPLETE
