# Scheduler integration: selected-day record layer

New record-scheduler.js binds to the caller's existing selected-day record. It does not create a separate store, save automatically, change revisions, migrate data or contact a backend. The existing ConnectCore block validator and free-time finder remain authoritative dependencies.

Operations: add/update/remove blocks, preserve existing IDs and metadata on edits, validate task links, reject overlaps, offer free slots, and reject stale selections. Returned values are copies. The controller must mark changes dirty, rerender and explicitly save through its existing adapter.

Ten regression tests are added to the release verification workflow. Test execution is pending until CI reports results. Serialization tests do not prove a live account save.

## Remaining UI wiring
Load ConnectCore and WorkstationFreeTime before this module. Bind after each successful day/account/demo load; dispose the previous scheduler when its record or account context is replaced, including sign-out. Route the existing block handlers and finder through this adapter, retaining the existing busy checks, dirty tracking, task controls and explicit save. Do not run the legacy finder UI handler and a replacement handler simultaneously.

This commit is the record-layer prerequisite, not a completed planner or APK integration. members/app.html and connect-app.js are intentionally unchanged. The new layer is not yet active in the installed APK. Next acceptance: UI wiring tests; day/account switch invalidation; linked-task preservation; no private-field loss; revision conflict handling and a real account save/reload. Drag/resize, sleep protection, undo and Morning handoff remain separate work.
