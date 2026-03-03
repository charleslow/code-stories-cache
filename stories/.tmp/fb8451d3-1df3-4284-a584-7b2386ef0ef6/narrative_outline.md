# Narrative Outline

## Chapter 0: Overview — "The Big Picture"
- **Label**: "The Big Picture"
- **Teaching point**: Yes, picoclaw natively supports Telegram. Introduce the channel architecture, key terms, and the answer to the query.
- **Snippets**: None (overview chapter)

## Chapter 1: Factory Self-Registration — "Plugging In"
- **Label**: "Plugging In"
- **Teaching point**: How Telegram registers itself without the Manager knowing about it — the init() + factory registry pattern.
- **Snippets**: `pkg/channels/telegram/init.go` (full file), `pkg/channels/registry.go` (RegisterFactory + getFactory)

## Chapter 2: Telegram Config — "Configuration"
- **Label**: "Configuration"
- **Teaching point**: What settings control the Telegram channel — token, proxy, allowlist, group triggers, placeholder config.
- **Snippets**: `pkg/config/config.go` (TelegramConfig struct), `config/config.example.json` (telegram section)

## Chapter 3: Bot Construction — "Building the Bot"
- **Label**: "Building the Bot"
- **Teaching point**: How NewTelegramChannel constructs the bot with proxy support and sets up BaseChannel with options.
- **Snippets**: `pkg/channels/telegram/telegram.go` lines 41-97 (struct + constructor)

## Chapter 4: Persistent Connection — "Long Polling"
- **Label**: "Long Polling"
- **Teaching point**: How Start() establishes the persistent connection via long polling (not webhooks), and why this design suits a personal agent.
- **Snippets**: `pkg/channels/telegram/telegram.go` lines 99-158 (Start method)

## Chapter 5: Inbound Message Handling — "Receiving Messages"
- **Label**: "Receiving Messages"
- **Teaching point**: How handleMessage processes a Telegram update — builds SenderInfo, checks allowlist, extracts content and media.
- **Snippets**: `pkg/channels/telegram/telegram.go` lines 405-466 (first half of handleMessage, up to media extraction)

## Chapter 6: Group Chat Filtering — "Group Triggers"
- **Label**: "Group Triggers"
- **Teaching point**: How group chats are filtered — mention detection, prefix matching, and the ShouldRespondInGroup logic.
- **Snippets**: `pkg/channels/telegram/telegram.go` lines 518-528 (group trigger in handleMessage), `pkg/channels/base.go` lines 132-158 (ShouldRespondInGroup)

## Chapter 7: Message Bus — "The Bus"
- **Label**: "The Bus"
- **Teaching point**: How the MessageBus decouples channels from the agent — buffered Go channels for inbound/outbound.
- **Snippets**: `pkg/bus/bus.go` lines 16-48 (struct, NewMessageBus, PublishInbound)

## Chapter 8: Outbound Dispatch — "Routing Replies"
- **Label**: "Routing Replies"
- **Teaching point**: How the Manager dispatches outbound messages to the right channel worker with rate limiting.
- **Snippets**: `pkg/channels/manager.go` lines 437-452 (newChannelWorker), `pkg/channels/manager.go` lines 456-482 (runWorker)

## Chapter 9: Send with Pre-Send Pipeline — "Typing & Placeholders"
- **Label**: "Typing & Placeholders"
- **Teaching point**: The preSend pipeline — stop typing, undo reactions, edit placeholder — before actually sending.
- **Snippets**: `pkg/channels/manager.go` lines 118-148 (preSend method)

## Chapter 10: Sending to Telegram — "Delivering the Reply"
- **Label**: "Delivering the Reply"
- **Teaching point**: How Send() converts markdown to Telegram HTML, and the HTML fallback if parsing fails.
- **Snippets**: `pkg/channels/telegram/telegram.go` lines 222-249 (Send method)

## Chapter 11: Typing Indicator — "Staying Alive"
- **Label**: "Staying Alive"
- **Teaching point**: How StartTyping refreshes the typing indicator every 4 seconds to keep it visible throughout the AI's processing time.
- **Snippets**: `pkg/channels/telegram/telegram.go` lines 255-279 (StartTyping method)

## Chapter 12: Media Handling — "Photos & Files"
- **Label**: "Photos & Files"
- **Teaching point**: How SendMedia dispatches images, audio, video, and documents using type-switched Telegram API calls.
- **Snippets**: `pkg/channels/telegram/telegram.go` lines 326-403 (SendMedia, focusing on the type switch)

## Chapter 13: Bot Commands — "Slash Commands"
- **Label**: "Slash Commands"
- **Teaching point**: How Telegram bot commands (/start, /help, /show, /list) are registered and handled.
- **Snippets**: `pkg/channels/telegram/telegram_commands.go` lines 13-30 (TelegramCommander interface + constructor), lines 56-65 (Start command)

## Chapter 14: Capability Interfaces — "Optional Powers"
- **Label**: "Optional Powers"
- **Teaching point**: How the interface-based capability system lets Manager discover what each channel supports at runtime.
- **Snippets**: `pkg/channels/interfaces.go` (full file, 42 lines)

## Chapter 15: Summary — "Wrapping Up"
- **Label**: "Wrapping Up"
- **Teaching point**: Synthesis of the full Telegram integration story, the "no sidecar needed" conclusion, and design takeaways.
- **Snippets**: None (summary chapter)

STAGE_2_COMPLETE
