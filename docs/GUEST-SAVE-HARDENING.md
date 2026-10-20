# Guest flow and save hardening

2026-10-20. This supersedes the earlier saveState MutationObserver cleanup mechanism in guest-continuation.js. No production data or authentication policy is changed by the source commit.

## Fixes
- Synchronize the plan.priority form field after guest staging so existing capture-on-save cannot overwrite an imported priority with its old empty value.
- Guard against repeated import clicks while identity validation is pending.
- Save feedback wraps the existing explicit save handler and waits for its completion. Account/demo successes are distinguished. Changed context/day results are ignored rather than overwriting the new destination status. Failed/unconfirmed saves retain edits and never emit save-complete.
- Emit workstation:save-complete after the existing action releases its busy lock; guest cleanup then verifies identity and the saved transfer marker with database read-back.
- Recheck the latest browser copy, account and day before removing it. A failed read-back keeps the copy and offers manual receipt retry.
- Keep guest continuation buttons after importing a recovery file; separate kept-plan and current-page downloads.
- Day switching warns about unadded form drafts. Existing unsaved-record confirmation remains in the original app handler.

## Evidence
Seven isolated guardedSave scenarios passed before proposing this batch. Added repository tests include an eighth day-change scenario, guest merge tests and source wiring checks. Those additional tests and CI are not claimed passed until executed. Source wiring tests do not substitute for a browser journey.

## Remaining
Browser/storage/real-account acceptance remains open; manual checking is user-led. SMTP/signup/backend password policy, full backup/restore, APK signing/install, recurring routines, learning handoffs, reminders and Muse are not closed by this batch.
