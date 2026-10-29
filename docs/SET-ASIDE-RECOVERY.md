# Persistent set-aside recovery

## Source change
New same-day set-aside actions preserve the previous area inside each existing task as workstationSetAside, version 1, previousAreaPresent and previousArea. If the original task had no area field, previousArea is null and restoration removes that field rather than inventing a category. Save selected day is required to persist the task and recovery metadata. Demo data remains memory-only. No new table, background migration or automatic save is introduced.

Restore selected original areas applies only to tasks currently in Set aside with supported recovery metadata. It restores the recorded area, removes this module's metadata and remains an unsaved edit until explicit saving. Older/manual set-aside tasks without metadata show that their original area is unavailable; Edit task can choose a replacement but this is not historical recovery. Unsupported metadata versions remain intact. If a user manually changes the area and later explicitly sets the task aside again, the latest current area becomes the recovery point for that new action.

Both operations preserve task IDs, completion state, schedule blocks, milestone links and unrelated task fields. Local undo restores the previous area and metadata shape only while the loaded account/day/task fingerprint remains unchanged. Persistent per-task recovery is separate from that local undo. All selections are preflighted before mutations; user text is rendered as text, not HTML. The existing cross-day move module loader is retained.

## Deployment receipts established earlier in this conversation
- Supabase reported muse-bridge-209-v5 version 2 ACTIVE after the corrected import-map deployment. This establishes deployment, not successful rule retrieval or Muse adoption. The prepared consumer integration ZIP is not installed on Muse's VM and its real runtime loader still needs configuration.
- Supabase apply_migration returned success for intentional_move_tasks_v1. No task-move call, record mutation or acceptance check was performed. Linked schedule/milestone/focus tasks remain excluded by the installed function.

## Remaining boundaries
No tests, browser/device checks, deployment probes, background polling, APK build/install or record mutation were performed for this source batch. The existing save RPC accepts plan JSON, but this batch does not claim runtime persistence or recovery acceptance. File-copy handoffs intentionally reconstruct only text/area; they do not preserve this metadata. The transactional full-task move preserves task JSON when eligible. Accounts, homepage wording, navigation, publisher configuration and credentials are unchanged.
