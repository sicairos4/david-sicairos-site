# Cross-day saved-task move interface

## Source status

Adds cross-day-move.js through the existing lighter-day-actions.js loader. The transactional SQL foundation is separately recorded in supabase/intentional_move_tasks_v1.sql. This source batch does not install that function, call it, move records, run tests or establish deployment/live acceptance. Backend activation requires its own exact approval.

## User flow

Select 1–100 unfinished tasks and a different destination date. Preview authenticates the account and reads saved source/target values. The local comparison includes bound form values and routine checks, not just A.record, because text-field edits can be unsaved outside that record object. ConnectCore.matchesSaved compares normalized saved content and the expected revision. Any difference requires explicit Save selected day first; no silent save/discard is performed.

The initial eligibility checks reject known milestone, schedule and active-focus links, preserving these tasks unchanged. Preview shows selected task text, dates and revisions. It does not display journals or lessons even though they are read privately in the browser to establish exact saved-state equality.

Move and save both days requires explicit confirmation and makes one pinned-token RPC call to intentional_move_tasks_v1. There is no client-side two-save fallback. The server transaction remains responsible for final revision and eligibility checks. A successful receipt includes both incremented revisions and selected IDs; no new live acceptance check is implied. The loaded source is now stale, so the interface instructs the user to reload before further edits. The existing reload control retains its own unsaved-work confirmation.

## Reversal and uncertainty

A page-session reverse action swaps dates and revision receipts and uses the same transactional endpoint. It requires unchanged local context and both server revisions; server-side changes reject reversal. It is not persistent or unconditional undo. Reload/account/day changes clear the page-session reversal receipt. A target day created by the move is not deleted by reversal.

Network errors, unrecognized server errors and unexpected receipts are treated conservatively as uncertain. No automatic write retry occurs. Users must preserve edits and reconcile saved days before proceeding. Expected SQL rejections stop the transaction; backend-not-installed errors explain the separate activation requirement. Concurrent local edits invalidate the preview rather than being silently overwritten. Existing planner saves retain their own revision-conflict protection.

Known scope: only supported existing task links are guarded. No blanket reconciliation of future metadata references, block rescheduling or milestone migration is claimed. Tests, browser/device checks, deployment checks and workflow dispatch remain skipped. No Muse task polling or policy adoption claim is included in this batch.
