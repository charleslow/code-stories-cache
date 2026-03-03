# Reviewed Narrative Outline

## Review Checklist

1. Each chapter has one clear teaching point? ✅ Yes
2. Technical terms introduced before use? ✅ Overview defines channel, bus, manager, long polling, plugin registry
3. Logical progression? ✅ Registration → Config → Construction → Connection → Interface → Capabilities → Inbound → Bus → Outbound → Send → Typing → Placeholder → Commands → Media → Summary
4. Redundant chapters? ✅ No redundancy — each covers a distinct aspect
5. Initialization, execution, key mechanisms? ✅ Covered
6. Final chapter prose-only summary? ✅ Chapter 15
7. Narrative arc? ✅ Setup phase → Runtime phase → Features phase
8. Smooth transitions? Will need explicit bridges between phases
9. Debug/logging code? Need to plan snippet ranges carefully to avoid logging-heavy sections
10. Query coverage? ✅
    - "Does picoclaw support telegram integration?" → Answered YES (chapters 0-5)
    - "If yes, explain how" → Full walkthrough (chapters 1-15)
    - "persistent connection" → Chapter 5 (long polling)
    - "telegram sidecar" → Overview explains why no sidecar needed
    - Note: The query asks "if no, how to build a sidecar" — since the answer is YES, the story explains the native approach instead. The overview should acknowledge the sidecar question and explain why it's unnecessary.

## Revised Outline (16 chapters)

Same structure as before but with explicit transition notes:

- Ch 0 → Ch 1: "Let's see how Telegram finds its way into the system"
- Ch 4 → Ch 5: "With the bot constructed, it needs a persistent connection"
- Ch 5 → Ch 6: "Now that we see how Telegram connects, let's look at the contract it must fulfill"
- Ch 8 → Ch 9: "The message has been shaped — now it needs to travel to the agent"
- Ch 10 → Ch 11: "With the worker ready, let's see what happens when Telegram actually sends"
- Ch 13 → Ch 14: "Beyond message flow, Telegram offers interactive controls"

## Snippet Line Budget Check (preliminary)

- Ch 1: registry.go (33 lines) + init.go (13 lines) = 46 lines ✅
  - Reduce: registry.go has imports that aren't essential. Show lines 10-32 = 23 lines. Total: 36 ✅
- Ch 2: helpers.go (~13 lines) + manager.go (~3 lines) = ~16 lines — too small, expand manager context
  - Show helpers.go 16-28 (13 lines) + manager.go 206-211 (6 lines) = 19 lines ✅
- Ch 3: config.go 237-246 (10 lines) ✅
- Ch 4: telegram.go 41-97 (57 lines) ✅
- Ch 5: telegram.go 99-158 (60 lines) — heavy on logging. Need to trim.
  - Show 99-116 (long polling start) + 125-157 (handler registration + start) = 50 lines. But some debug logging in between. Better: show 99-117 (19 lines) + 125-157 (33 lines) = 52 lines ✅
- Ch 6: base.go 43-93 (51 lines) ✅
- Ch 7: interfaces.go full (42 lines) ✅
- Ch 8: telegram.go 405-440 + 517-565 — need to be selective. Show 405-433 (sender/allowlist) + 517-565 (group + publish) = 72 lines. Trim to fit.
  - Better: 405-433 (29 lines) + 538-565 (28 lines) = 57 lines ✅
- Ch 9: bus.go 16-59 (44 lines) ✅
- Ch 10: manager.go 590-608 (19 lines) + 437-452 (16 lines) = 35 lines ✅
- Ch 11: telegram.go 222-249 (28 lines) ✅
- Ch 12: telegram.go 255-279 (25 lines) ✅
- Ch 13: telegram.go 301-323 (23 lines) + manager.go 118-148 (31 lines) = 54 lines ✅
- Ch 14: telegram_commands.go 13-54 (42 lines) ✅
- Ch 15: telegram.go 326-403 (78 lines) — too many! Trim.
  - Show 326-340 (setup, 15 lines) + 360-391 (switch dispatch, 32 lines) = 47 lines ✅

All within budget.

STAGE_3_COMPLETE
