# Exploration Read Notes

## Answer: YES, picoclaw has full Telegram integration

Telegram is a **first-class channel** in picoclaw, not a sidecar. It uses the `telego` library for the Telegram Bot API.

## Entry Points & Control Flow

1. **Gateway startup** (`cmd/picoclaw/internal/gateway/helpers.go`):
   - Loads config → Creates MessageBus → Creates AgentLoop → Creates ChannelManager
   - Blank imports (`_ "github.com/sipeed/picoclaw/pkg/channels/telegram"`) trigger `init()` factory registration
   - ChannelManager.initChannels() checks `config.Channels.Telegram.Enabled && Token != ""`
   - Calls `initChannel("telegram", "Telegram")` which looks up the registered factory

2. **Factory Registration** (`pkg/channels/telegram/init.go`):
   - `init()` calls `channels.RegisterFactory("telegram", func(...) { NewTelegramChannel(cfg, bus) })`
   - Pure plugin pattern — Manager never imports telegram package directly

3. **Channel Construction** (`pkg/channels/telegram/telegram.go` — `NewTelegramChannel`):
   - Creates `telego.Bot` with optional proxy support (config or env)
   - Creates `BaseChannel` with options: MaxMessageLength(4096), GroupTrigger, ReasoningChannelID
   - Creates TelegramCommands for bot slash commands

4. **Starting the Channel** (`TelegramChannel.Start`):
   - Initializes bot commands (rate-limit-aware — only updates if changed)
   - Starts `bot.UpdatesViaLongPolling` with 30s timeout — THIS IS THE PERSISTENT CONNECTION
   - Creates `BotHandler` and registers message handlers for /start, /help, /show, /list, and generic messages
   - Runs `bh.Start()` in a goroutine

5. **Inbound Message Flow**:
   - `handleMessage()` extracts sender info, checks allowlist
   - Downloads any media (photos, voice, audio, documents) via Telegram file API
   - Detects group vs private chat, applies group trigger filtering
   - Calls `BaseChannel.HandleMessage()` which:
     a. Auto-triggers typing indicator (TypingCapable)
     b. Auto-triggers reaction (ReactionCapable)
     c. Auto-sends placeholder message (PlaceholderCapable)
     d. Publishes InboundMessage to MessageBus

6. **Outbound Message Flow**:
   - Manager's dispatcher goroutine reads from bus.SubscribeOutbound
   - Routes to per-channel worker (channelWorker with queue + rate limiter)
   - Worker calls `sendWithRetry()` which:
     a. Rate-limits via `w.limiter.Wait()`
     b. Calls `preSend()` — stops typing, undoes reaction, tries editing placeholder
     c. If placeholder edit succeeds, skip Send
     d. Otherwise calls `ch.Send()` with retry (exponential backoff)
   - `TelegramChannel.Send()` converts markdown to Telegram HTML, sends via bot API

7. **Typing Indicator**:
   - `StartTyping()` sends ChatAction(typing) immediately, then repeats every 4s in goroutine
   - Returns cancel function, stored by Manager in sync.Map
   - TTL janitor cleans up stale entries every 10s

8. **Markdown → Telegram HTML**:
   - Custom `markdownToTelegramHTML()` function
   - Extracts code blocks and inline code first (placeholder approach to avoid double-processing)
   - Converts headings, blockquotes, bold, italic, strikethrough, lists, links
   - Falls back to plain text if HTML parse fails

EXPLORATION_READ
