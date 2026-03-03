# Exploration Read — Key File Notes

## Entry Points & Control Flow

### Channel Initialization Flow
1. `config.json` parsed → `Config.Channels.Telegram` populates `TelegramConfig`
2. `pkg/channels/telegram/init.go` registers "telegram" factory via `channels.RegisterFactory`
3. `Manager.initChannels()` checks `Telegram.Enabled && Telegram.Token != ""`, calls `m.initChannel("telegram", "Telegram")`
4. `initChannel` looks up factory, calls it, injects MediaStore/PlaceholderRecorder/Owner
5. `Manager.StartAll()` calls `channel.Start(ctx)` for each, creates workers, starts dispatcher goroutines

### Telegram Start Flow
1. `TelegramChannel.Start()` creates cancellable context
2. Calls `initBotCommands()` to register /start, /help, /show, /list with Telegram API
3. Starts long polling via `bot.UpdatesViaLongPolling(ctx, timeout=30)` — this is the persistent connection
4. Creates `BotHandler`, registers command handlers and a catch-all `AnyMessage()` handler
5. Starts BotHandler in a goroutine

### Inbound Message Flow
1. Telegram long poll delivers update → `handleMessage()` called
2. Builds `SenderInfo` with canonical ID "telegram:<user_id>"
3. Checks allowlist via `IsAllowedSender()`
4. Downloads media (photos, voice, audio, docs) via `downloadPhoto/downloadFile`
5. For group chats: applies group trigger filtering (mention detection, prefix matching)
6. Calls `BaseChannel.HandleMessage()` which auto-triggers typing, reaction, placeholder
7. `BaseChannel.HandleMessage()` publishes `InboundMessage` to MessageBus

### Outbound Message Flow
1. Agent publishes `OutboundMessage` to bus
2. Manager's `dispatchOutbound` goroutine reads from bus, routes to channel worker queue
3. Worker's `runWorker` splits messages if > 4096 chars (Telegram limit)
4. `sendWithRetry` does rate limiting (20 msg/s for Telegram), calls `preSend` (stop typing, edit placeholder), then `ch.Send()`
5. `TelegramChannel.Send()` converts markdown to Telegram HTML, sends via bot API

### Persistent Connection Mechanism
- Long polling with 30-second timeout: `bot.UpdatesViaLongPolling(ctx, &telego.GetUpdatesParams{Timeout: 30})`
- Context-based cancellation for clean shutdown
- No reconnection logic in picoclaw itself — the `telego` library handles polling loop internally

## Key Design Decisions
- Factory pattern with `init()` self-registration — zero coupling between Manager and channel implementations
- BaseChannel embeds shared logic (allowlist, group triggers) — channels only implement platform-specific parts
- Optional capabilities via interface type assertions (TypingCapable, PlaceholderCapable, etc.)
- MessageBus decouples inbound/outbound — agent doesn't know about channels
- Markdown→HTML conversion handles Telegram's limited HTML subset
- Rate limiting per-channel (Telegram: 20 msg/s) with exponential backoff retry

EXPLORATION_READ
