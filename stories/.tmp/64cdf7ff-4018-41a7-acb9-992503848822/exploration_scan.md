# Exploration Scan

## Relevant Files for Telegram Integration

### Core Telegram Channel
- `pkg/channels/telegram/telegram.go` — Main TelegramChannel struct, Start/Stop, Send, message handling, long polling, markdown→HTML conversion
- `pkg/channels/telegram/init.go` — Factory registration via `init()`
- `pkg/channels/telegram/telegram_commands.go` — Bot commands (/start, /help, /show, /list)

### Channel Framework
- `pkg/channels/base.go` — BaseChannel struct, Channel interface, HandleMessage, allowlist, group trigger logic
- `pkg/channels/manager.go` — Manager orchestrates all channels, per-channel workers, rate limiting, retry, placeholder/typing lifecycle
- `pkg/channels/registry.go` — Plugin registry for channel factories
- `pkg/channels/interfaces.go` — Optional interfaces: TypingCapable, MessageEditor, PlaceholderCapable, ReactionCapable, PlaceholderRecorder

### Message Bus
- `pkg/bus/bus.go` — MessageBus with inbound/outbound/media channels
- `pkg/bus/types.go` — InboundMessage, OutboundMessage, SenderInfo, Peer, MediaPart

### Configuration
- `pkg/config/config.go` — TelegramConfig struct, ChannelsConfig
- `pkg/config/defaults.go` — Default config values
- `config/config.example.json` — Example configuration

### Gateway (Entry Point)
- `cmd/picoclaw/internal/gateway/helpers.go` — Gateway startup, wires bus/channels/agent/heartbeat
- `cmd/picoclaw/internal/gateway/command.go` — Cobra command definition

### Persistent Connection / Heartbeat
- `pkg/heartbeat/service.go` — HeartbeatService for periodic proactive messages via channels

### Routing/Session
- `pkg/routing/session_key.go` — Session key construction for DM/group scoping

EXPLORATION_SCANNED
