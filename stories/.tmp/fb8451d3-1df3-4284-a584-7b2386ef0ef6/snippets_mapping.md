# Snippets Mapping

## Chapter 0: Overview
- No snippets

## Chapter 1: Plugging In
- Snippet A: `pkg/channels/telegram/init.go` lines 1-13 (13 lines) — full file
- Snippet B: `pkg/channels/registry.go` lines 1-32 (32 lines) — full file
- Total: 45 lines

## Chapter 2: Configuration
- Snippet A: `pkg/config/config.go` lines 237-246 (10 lines) — TelegramConfig struct
- Snippet B: `config/config.example.json` lines 49-57 (9 lines) — telegram JSON
- Total: 19 lines

## Chapter 3: Building the Bot
- Snippet A: `pkg/channels/telegram/telegram.go` lines 41-97 (57 lines) — struct + NewTelegramChannel
- Total: 57 lines

## Chapter 4: Long Polling
- Snippet A: `pkg/channels/telegram/telegram.go` lines 99-157 (59 lines) — Start method
- Total: 59 lines

## Chapter 5: Receiving Messages
- Snippet A: `pkg/channels/telegram/telegram.go` lines 405-454 (50 lines) — first half of handleMessage
- Total: 50 lines

## Chapter 6: Group Triggers
- Snippet A: `pkg/channels/telegram/telegram.go` lines 518-528 (11 lines) — group check in handleMessage
- Snippet B: `pkg/channels/base.go` lines 132-158 (27 lines) — ShouldRespondInGroup
- Total: 38 lines

## Chapter 7: The Bus
- Snippet A: `pkg/bus/bus.go` lines 16-48 (33 lines) — struct + NewMessageBus + PublishInbound
- Total: 33 lines

## Chapter 8: Routing Replies
- Snippet A: `pkg/channels/manager.go` lines 437-452 (16 lines) — newChannelWorker
- Snippet B: `pkg/channels/manager.go` lines 456-482 (27 lines) — runWorker
- Total: 43 lines

## Chapter 9: Typing & Placeholders
- Snippet A: `pkg/channels/manager.go` lines 118-148 (31 lines) — preSend
- Total: 31 lines

## Chapter 10: Delivering the Reply
- Snippet A: `pkg/channels/telegram/telegram.go` lines 222-249 (28 lines) — Send method
- Total: 28 lines

## Chapter 11: Staying Alive
- Snippet A: `pkg/channels/telegram/telegram.go` lines 255-279 (25 lines) — StartTyping
- Total: 25 lines

## Chapter 12: Photos & Files
- Snippet A: `pkg/channels/telegram/telegram.go` lines 326-403 (78 lines) — SendMedia
- Total: 78 lines (at the limit; the method is a single logical unit)

## Chapter 13: Slash Commands
- Snippet A: `pkg/channels/telegram/telegram_commands.go` lines 13-30 (18 lines) — interface + constructor
- Snippet B: `pkg/channels/telegram/telegram_commands.go` lines 56-65 (10 lines) — Start command
- Total: 28 lines

## Chapter 14: Optional Powers
- Snippet A: `pkg/channels/interfaces.go` lines 1-42 (42 lines) — full file
- Total: 42 lines

## Chapter 15: Summary
- No snippets

STAGE_4_COMPLETE
