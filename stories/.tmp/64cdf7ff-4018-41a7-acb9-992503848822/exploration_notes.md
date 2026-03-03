# Exploration Notes — Picoclaw Telegram Integration

## Core Data Structures
- **TelegramChannel**: Embeds BaseChannel, holds telego.Bot, BotHandler, commands, chatIDs map
- **BaseChannel**: Generic channel with allowlist, running state (atomic.Bool), bus reference, groupTrigger, mediaStore, placeholderRecorder, owner
- **Manager**: Holds channels map, workers map (per-channel queue + rate limiter), bus, shared HTTP server, placeholder/typing/reaction sync.Maps
- **MessageBus**: Three buffered channels (inbound, outbound, outboundMedia) + done signal

## Design Patterns
1. **Plugin Registry**: Channels self-register via Go's `init()` mechanism. Manager never imports channel packages — blank imports in gateway trigger registration. This is idiomatic Go plugin architecture.
2. **Composition over Inheritance**: TelegramChannel embeds BaseChannel for shared behavior. Optional capabilities use Go interfaces (TypingCapable, PlaceholderCapable, etc.) checked via type assertion.
3. **Pub/Sub Decoupling**: MessageBus decouples channels from agent loop. Channels publish inbound → bus → agent loop consumes. Agent publishes outbound → bus → dispatcher routes to channel workers.
4. **Worker-per-Channel**: Each channel gets its own goroutine + buffered queue + rate limiter. Isolates slow channels from fast ones.
5. **Retry with Error Classification**: ErrNotRunning/ErrSendFailed = permanent (no retry), ErrRateLimit = fixed delay, ErrTemporary = exponential backoff.

## Key "Why" Decisions
- **Long polling over webhooks**: Telegram channel uses `UpdatesViaLongPolling` (30s timeout). This is intentional — picoclaw is designed as a personal agent that runs on any machine (even behind NAT), so it doesn't need a public URL for webhooks.
- **Rate-limit-aware command registration**: `initBotCommands()` compares current vs desired commands and only calls `SetMyCommands` if they differ. Telegram aggressively rate-limits this endpoint.
- **Placeholder edit pattern**: Instead of "thinking..." → delete → new message, picoclaw sends a placeholder and edits it in-place when the response arrives. Less visual noise for the user.
- **Typing ticker at 4s**: Telegram's typing indicator expires after ~5 seconds, so 4s gives safe overlap without excessive API calls.
- **Code block extraction before markdown conversion**: The markdown→HTML converter extracts fenced code blocks and inline code first, replacing them with null-byte placeholders. This prevents the markdown regex patterns from corrupting code content.
- **TTL janitor for cleanup**: Stale typing/placeholder entries are cleaned up by a 10s ticker, preventing memory leaks when the outbound path fails (e.g., LLM errors).

## Architectural Insights
- The whole system is designed for multi-channel operation — Telegram is just one of ~15 supported channels
- The persistent connection is inherent in the long-polling design — no separate "sidecar" needed
- Heartbeat service can proactively send messages through any channel, including Telegram
- Session routing supports per-peer, per-channel-peer, and cross-platform identity linking

STAGE_1_COMPLETE
