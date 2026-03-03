# Narrative Outline

## Chapter 0: Overview — "Telegram's Home in PicoClaw"
- Label: "Overview"
- Snippets: none
- Teaching point: Orient the reader — yes, Telegram is a first-class channel, explain the key concepts (channel, bus, manager, long polling, plugin registry)

## Chapter 1: Plugin Registration — "How Channels Register"
- Label: "Plugin Registry"
- Snippets: `pkg/channels/registry.go` (full file), `pkg/channels/telegram/init.go` (full file)
- Teaching point: The Go `init()` pattern for self-registering plugins

## Chapter 2: Factory Activation — "Wiring Telegram into the Gateway"
- Label: "Factory Activation"
- Snippets: `cmd/picoclaw/internal/gateway/helpers.go` (blank imports ~16-28), `pkg/channels/manager.go` (initChannels telegram block ~209-211)
- Teaching point: How blank imports trigger init() and how the Manager activates telegram

## Chapter 3: Configuration — "What Telegram Needs to Start"
- Label: "Telegram Config"
- Snippets: `pkg/config/config.go` (TelegramConfig struct ~237-246)
- Teaching point: The config-driven approach — token, proxy, allowlist, group trigger, typing, placeholder

## Chapter 4: Channel Construction — "Building the Telegram Bot"
- Label: "Bot Construction"
- Snippets: `pkg/channels/telegram/telegram.go` (TelegramChannel struct + NewTelegramChannel ~41-97)
- Teaching point: How the telego bot is created with optional proxy, and BaseChannel is composed

## Chapter 5: The Persistent Connection — "Long Polling Keeps the Line Open"
- Label: "Long Polling"
- Snippets: `pkg/channels/telegram/telegram.go` (Start method ~99-158)
- Teaching point: Why long polling (not webhooks) for persistent connection, 30s timeout, handler registration

## Chapter 6: The Channel Interface — "The Contract Every Channel Must Fulfill"
- Label: "Channel Contract"
- Snippets: `pkg/channels/base.go` (Channel interface + BaseChannel struct ~43-93)
- Teaching point: The core interface and composition model (embed BaseChannel)

## Chapter 7: Optional Capabilities — "Typing, Placeholders, and More"
- Label: "Capability Interfaces"
- Snippets: `pkg/channels/interfaces.go` (full file, 42 lines)
- Teaching point: Go's interface-based capability negotiation — channels opt in by implementing interfaces

## Chapter 8: Handling Inbound Messages — "From Telegram Update to Bus Event"
- Label: "Inbound Pipeline"
- Snippets: `pkg/channels/telegram/telegram.go` (handleMessage ~405-440, ~456-565)
- Teaching point: How a Telegram update becomes an InboundMessage — sender extraction, allowlist, media download, group filtering

## Chapter 9: The Message Bus — "The Pub/Sub Highway"
- Label: "Message Bus"
- Snippets: `pkg/bus/bus.go` (MessageBus struct + PublishInbound + ConsumeInbound ~16-59)
- Teaching point: Buffered channels as a decoupling mechanism between channels and agent

## Chapter 10: Outbound Dispatch — "Routing Responses Back"
- Label: "Outbound Dispatch"
- Snippets: `pkg/channels/manager.go` (dispatchOutbound ~590-608, newChannelWorker ~437-452)
- Teaching point: Per-channel workers with rate limiters, generic dispatch loop

## Chapter 11: Sending Messages — "Markdown, HTML, and Fallbacks"
- Label: "Sending Messages"
- Snippets: `pkg/channels/telegram/telegram.go` (Send method ~222-249)
- Teaching point: Markdown → Telegram HTML conversion, fallback to plain text on parse failure

## Chapter 12: Typing Indicator — "The 4-Second Heartbeat"
- Label: "Typing Indicator"
- Snippets: `pkg/channels/telegram/telegram.go` (StartTyping ~255-279)
- Teaching point: Why 4-second ticker (Telegram's 5s expiry), goroutine lifecycle via context cancellation

## Chapter 13: Placeholder Pattern — "Edit, Don't Delete"
- Label: "Placeholder Edit"
- Snippets: `pkg/channels/telegram/telegram.go` (SendPlaceholder ~301-323), `pkg/channels/manager.go` (preSend ~118-148)
- Teaching point: Send-then-edit pattern for cleaner UX, how preSend orchestrates stop typing + undo reaction + edit

## Chapter 14: Bot Commands — "Interactive Controls"
- Label: "Bot Commands"
- Snippets: `pkg/channels/telegram/telegram_commands.go` (TelegramCommander interface + cmd struct + Help ~13-54)
- Teaching point: Bot slash commands as a control interface, how they're registered

## Chapter 15: Media Handling — "Photos, Voice, and Files"
- Label: "Media Handling"
- Snippets: `pkg/channels/telegram/telegram.go` (SendMedia ~326-403)
- Teaching point: Multi-type media dispatch (image/audio/video/file), media store integration

## Chapter 16: Summary — "The Full Picture"
- Label: "Summary"
- Snippets: none
- Teaching point: Recap — Telegram is natively integrated, no sidecar needed. Key design patterns.

STAGE_2_COMPLETE
