# Snippets Mapping

## Chapter 0: Overview
- Snippets: [] (none)

## Chapter 1: Plugin Registry
- Snippet 1: `pkg/channels/registry.go` lines 10-32 (23 lines) — ChannelFactory type, factories map, RegisterFactory, getFactory
- Snippet 2: `pkg/channels/telegram/init.go` lines 1-13 (13 lines) — Telegram's init() registration
- Total: 36 lines ✅

## Chapter 2: Factory Activation
- Snippet 1: `cmd/picoclaw/internal/gateway/helpers.go` lines 16-28 (13 lines) — Blank imports that trigger init()
- Snippet 2: `pkg/channels/manager.go` lines 166-178 + 184-199 — initChannel helper (factory lookup + dependency injection). Actually let's show 166-199 (34 lines) but that includes logging. Better: show 166-168 + 178 + 184-199, but can't skip lines in a snippet. Let me show two snippets.
  - Snippet 2a: `pkg/channels/manager.go` lines 166-168 (3 lines) — too short
  - Better approach: show `initChannels` block for telegram specifically
  - Snippet 2: `pkg/channels/manager.go` lines 206-211 (6 lines) — initChannels telegram check
- Total: 19 lines — a bit short but acceptable for a simple chapter

## Chapter 3: Telegram Config
- Snippet 1: `pkg/config/config.go` lines 237-246 (10 lines) — TelegramConfig struct
- Total: 10 lines ✅

## Chapter 4: Bot Construction
- Snippet 1: `pkg/channels/telegram/telegram.go` lines 41-97 (57 lines) — TelegramChannel struct + NewTelegramChannel
- Total: 57 lines ✅

## Chapter 5: Long Polling (Persistent Connection)
- Snippet 1: `pkg/channels/telegram/telegram.go` lines 99-117 (19 lines) — Start method up to long polling init
- Snippet 2: `pkg/channels/telegram/telegram.go` lines 125-157 (33 lines) — Handler registration and goroutine start
- Total: 52 lines ✅

## Chapter 6: Channel Interface
- Snippet 1: `pkg/channels/base.go` lines 43-52 (10 lines) — Channel interface
- Snippet 2: `pkg/channels/base.go` lines 81-112 (32 lines) — BaseChannel struct + NewBaseChannel
- Total: 42 lines ✅

## Chapter 7: Capability Interfaces
- Snippet 1: `pkg/channels/interfaces.go` lines 1-42 (42 lines) — Full file
- Total: 42 lines ✅

## Chapter 8: Inbound Pipeline
- Snippet 1: `pkg/channels/telegram/telegram.go` lines 405-433 (29 lines) — handleMessage: nil checks, sender extraction, allowlist
- Snippet 2: `pkg/channels/telegram/telegram.go` lines 517-565 (49 lines) — group filtering + publish. That's a lot. Trim to 538-565 (28 lines)
- Total: 57 lines ✅

## Chapter 9: Message Bus
- Snippet 1: `pkg/bus/bus.go` lines 16-59 (44 lines) — MessageBus struct + PublishInbound + ConsumeInbound
- Total: 44 lines ✅

## Chapter 10: Outbound Dispatch
- Snippet 1: `pkg/channels/manager.go` lines 437-452 (16 lines) — newChannelWorker
- Snippet 2: `pkg/channels/manager.go` lines 590-608 (19 lines) — dispatchOutbound
- Total: 35 lines ✅

## Chapter 11: Sending Messages
- Snippet 1: `pkg/channels/telegram/telegram.go` lines 222-249 (28 lines) — Send method
- Total: 28 lines ✅

## Chapter 12: Typing Indicator
- Snippet 1: `pkg/channels/telegram/telegram.go` lines 255-279 (25 lines) — StartTyping
- Total: 25 lines ✅

## Chapter 13: Placeholder Edit
- Snippet 1: `pkg/channels/telegram/telegram.go` lines 298-323 (26 lines) — SendPlaceholder (with doc comment)
- Snippet 2: `pkg/channels/manager.go` lines 116-148 (33 lines) — preSend
- Total: 59 lines ✅

## Chapter 14: Bot Commands
- Snippet 1: `pkg/channels/telegram/telegram_commands.go` lines 13-54 (42 lines) — TelegramCommander interface + cmd struct + NewTelegramCommands + commandArgs + Help
- Total: 42 lines ✅

## Chapter 15: Media Handling
- Snippet 1: `pkg/channels/telegram/telegram.go` lines 326-340 (15 lines) — SendMedia setup
- Snippet 2: `pkg/channels/telegram/telegram.go` lines 360-391 (32 lines) — switch dispatch for media types
- Total: 47 lines ✅

## Chapter 16: Summary
- Snippets: [] (none)

STAGE_4_COMPLETE
