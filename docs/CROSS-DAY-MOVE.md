# Atomic cross-day task move — foundation

## Status
SQL source only. This batch does not apply a migration, enable a UI, move records, run tests or establish live acceptance. The metadata query read intentional_days column definitions and intentional_save_day source, not personal planner rows.

## Contract
intentional_move_tasks_v1(from day, to day, task IDs, expected source revision, expected target revision) derives the account from auth.uid(). It locks both days in date order using the existing save RPC's advisory-lock expression. It verifies both expected revisions and calls intentional_save_day twice inside one transaction. Any failure rolls both changes back. Existing plan size checks, journal/lesson limits and revision updates remain in the save RPC. Existing journals, lessons and unrelated plan fields are preserved. An absent target requires a null target revision and starts with empty task/block/milestone arrays. No other account can be selected by an argument.

The initial scope is 1–100 unfinished tasks without known schedule, milestone or active-focus links. Linked tasks fail rather than losing those links. Whole selected task JSON objects and original IDs move; there is no text/area reconstruction or silent duplicate merge. Target ID collisions fail. Source and target task order is retained; moved tasks append in source order. Arbitrary future task-reference formats are not claimed to be reconciled.

## Reversal and uncertain results
A guarded reversal can call the same function with the days swapped, the same IDs and the two revision receipts swapped. Both dates must still have those exact revisions and the tasks must remain eligible. This is not unconditional undo. A missing target created by the move remains as an empty saved day after reversal; no saved day is deleted.

If a request times out, do not auto-retry or claim failure. Read both saved revisions and task IDs through the authenticated UI, then reconcile the outcome. Expected revision checks prevent a repeated successful request from silently applying again, but there is no durable operation-ID receipt ledger in this foundation.

## Next implementation
1. Obtain separate authorization to install this migration. CREATE FUNCTION deliberately fails if the name already exists; do not overwrite an uninspected implementation. Apply as one transaction so grants are not left partially configured.
2. Add authenticated destination loading and explicit saved-state comparison; refuse unsaved source edits rather than discarding or implicitly saving them.
3. Preview chosen tasks, dates, exclusions and revision expectations. Clearly state the action saves both account days, unlike ordinary local edits.
4. Require explicit move confirmation, make one RPC call, handle uncertain outcomes without automatic retry and show the returned revision receipt.
5. Reload through the existing planner after success; offer guarded reverse only with unchanged revisions.
6. Extend linked milestone/schedule handling only after its semantics are explicitly implemented.

No service-role key, anonymous write access, new table, credential change or source-record mutation occurs merely by committing these files. Runtime tests and acceptance remain deferred under the user's instruction.
