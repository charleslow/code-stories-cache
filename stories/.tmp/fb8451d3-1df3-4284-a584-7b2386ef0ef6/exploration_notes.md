# Exploration Notes — Full Synthesis

## Answer to the Query
**Yes, picoclaw natively supports Telegram integration.** It is a first-class built-in channel, not a sidecar or plugin. No separate process is needed.

## Core Data Structures
- `TelegramChannel` embeds `BaseChannel` and wraps the `telego.Bot` and `th.BotHandler`
- `BaseChannel` holds shared state: allowlist, group trigger config, running flag (atomic.Bool), media store, placeholder recorder
- `MessageBus` is three buffered Go channels (inbound, outbound, outboundMedia) with context-aware pub/sub
- `Manager` owns a map of channels and per-channel workers with rate limiters

## Design Patterns
1. **Factory Registry** — Each channel self-registers via `init()`. Manager discovers channels through the registry, not imports.
2. **Capability Interfaces** — Optional features (TypingCapable, PlaceholderCapable, MediaSender, MessageEditor) are discovered via Go type assertions at runtime
3. **Composition over Inheritance** — TelegramChannel embeds BaseChannel for shared behavior
4. **Worker Pool per Channel** — Each channel gets a dedicated goroutine with a buffered queue and rate limiter
5. **Pre-send Pipeline** — Before sending a response, Manager stops typing, undoes reactions, and tries editing the placeholder message

## Interesting "Why" Decisions
- **Long polling over webhooks**: Telegram channel uses polling mode (`UpdatesViaLongPolling`) rather than webhooks. This means no public URL or TLS cert is needed — ideal for a "personal AI agent" that runs on a local machine, Raspberry Pi, or behind NAT.
- **30-second timeout**: The polling timeout of 30s is the Telegram API's max, maximizing efficiency (fewer HTTP requests while remaining responsive).
- **Bot commands rate-limit check**: `initBotCommands` compares current commands with desired ones before calling SetMyCommands, avoiding Telegram's rate limit that triggers when setting commands on every restart.
- **Typing indicator refresh loop**: Telegram's typing indicator expires after ~5 seconds, so `StartTyping` sends ChatAction every 4 seconds in a goroutine — a nice detail that keeps the UX responsive.
- **Markdown→HTML conversion with placeholder protection**: Code blocks and inline code are extracted and replaced with null-byte placeholders before HTML escaping, then restored — preventing double-escaping of code content.
- **TTL janitor for stale state**: If the agent fails or times out, leftover typing stops and placeholder entries are cleaned up by a background goroutine every 10 seconds.

STAGE_1_COMPLETE
