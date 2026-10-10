# Phoenix Genesis — Latest Checkpoint

## Checkpoint

- Feature: Outbound Telegram signal publishing and opportunity journaling
- Status: IMPLEMENTED — FULL TEST SUITE PASSED
- Git status: UNCOMMITTED
- Commit: PENDING
- Runtime mode: OBSERVE / PAPER
- Real orders: DISABLED

## Purpose

Publish approved BUY/SELL proposals from the operational runtime through the existing Phoenix Genesis Telegram bot. Record observed market opportunities separately for later analysis.

Telegram is an outbound signal-publication channel only. It does not receive commands or execute trades.

## Architecture

Operational Paper Runtime
-> SignalPublisher
-> SQLite Signal Journal and Notification Outbox
-> NotificationDispatcher
-> TelegramSender

Operational Paper Runtime
-> OpportunityObserver
-> OpportunityJournal (JSONL)

## Timestamp and Reference-Price Semantics

- `observed_at` records the market observation time associated with the reference price.
- `reference_price` is captured from that observation.
- `generated_at` records the timestamp supplied when the runtime publishes the proposal.
- `sent_at` is recorded only after successful Telegram delivery is confirmed.
- Delivery retries must not replace the original reference price, `observed_at`, or `generated_at`.

The delivery E2E test verifies distinct observation, publication, and successful-send timestamps and checks that the original reference price and timestamps remain unchanged after delivery.

## Reliability and Safety

- Persist approved signals and queued messages before delivery.
- Retry failed deliveries using bounded retry intervals.
- Mark a message SENT only after the Telegram API confirms success.
- Keep notification failures isolated from the trading runtime.
- Do not synthesize BUY/SELL signals from WAIT decisions.
- Telegram dispatch is disabled by default unless `PHOENIX_TELEGRAM_ENABLED=1`.
- The current dispatcher is invoked by the runtime; it is not a continuously running background worker.
- The implementation assumes a single dispatcher instance.
- Delivery may be duplicated if Telegram accepts a message but the response is lost.

## Verification Evidence

- Latest full test suite: 1335 passed in 29.07 seconds.
- Publisher and delivery E2E tests: 14 passed in 1.53 seconds.
- Dispatcher, sender, and outbox tests: 15 passed in 2.11 seconds.
- Runtime publisher tests: 2 passed in 0.50 seconds.
- The outbox tests cover persistence across store reopening and persisted retry state.
- A manual Telegram Bot API transport test was previously reported as successful.
- A successful transport test and fixture-based delivery E2E test do not establish that a genuine runtime-generated BUY/SELL signal has been delivered to Telegram.

## Known Limits and Deferred Work

- Real order execution remains disabled.
- Telegram dispatch remains opt-in and is not a continuous background service.
- Duplicate delivery remains possible if the API accepts a message but its response is lost.
- One-hour hypothetical outcome evaluation and evaluation on an opposite valid signal are separate work; they are not established by this publishing feature.
- The one-week signal evaluation workflow still requires its own verified outcome-recording and analysis lifecycle.

## Next Action

Review the development-history diff and the complete working-tree changes. Verify the final documentation against test evidence, then request explicit approval before committing.
