# Exploration Scan — Telegram Integration in PicoClaw

## Relevant Files

### Telegram Channel (core)
- `pkg/channels/telegram/telegram.go` — Main Telegram channel implementation (TelegramChannel struct, Start, Stop, Send, handleMessage, long polling, markdown conversion, media)
- `pkg/channels/telegram/init.go` — Factory self-registration via init()
- `pkg/channels/telegram/telegram_commands.go` — Bot commands: /start, /help, /show, /list

### Channel Framework
- `pkg/channels/base.go` — BaseChannel shared logic (allowlist, group triggers, HandleMessage)
- `pkg/channels/manager.go` — Manager: lifecycle, rate limiting, retry, dispatch, workers, preSend
- `pkg/channels/registry.go` — ChannelFactory registration (RegisterFactory, getFactory)
- `pkg/channels/interfaces.go` — Optional capability interfaces (TypingCapable, MessageEditor, PlaceholderCapable, ReactionCapable, PlaceholderRecorder)
- `pkg/channels/webhook.go` — WebhookHandler and HealthChecker interfaces
- `pkg/channels/media.go` — MediaSender interface

### Message Bus
- `pkg/bus/bus.go` — MessageBus: buffered channels for inbound/outbound/media
- `pkg/bus/types.go` — Message types: InboundMessage, OutboundMessage, Peer, SenderInfo, MediaPart

### Config
- `pkg/config/config.go` — TelegramConfig struct, ChannelsConfig
- `pkg/config/defaults.go` — Default Telegram config values
- `config/config.example.json` — Example JSON config with Telegram section

### Heartbeat (persistent connection companion)
- `pkg/heartbeat/service.go` — HeartbeatService for periodic checks, sends to last-active channel

EXPLORATION_SCANNED
