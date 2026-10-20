# Existing day tools: integration and acceptance

Inspection on 2026-10-19 found assets/workstation/day-tools.js already implementing habits, a private notebook and a same-day export merge. The inspected morning-template-refresh loader did not include it. Repository code search returned incomplete results, so absence of every other possible loader reference is not asserted.

This batch explicitly loads day-tools.js alongside carry-forward.js, skips an already-present script URL, and preserves the module's own dayToolsHabits mounting guard. It reuses existing implementation rather than building a parallel habit/restore system. No runtime acceptance is claimed.

## Existing supported functions

- Morning: day-specific habits with a cue, minimum action and unrecorded/done/partial/skipped states. Habit completion remains distinct from task completion.
- Journal: private brain dump and named notebook entries.
- Settings: local preview of a matching-day export and explicit ownership confirmation before merging supported entries into unsaved work. No account write until Save selected day.
- Restore rejects conflicting IDs, invalid links, overlapping schedule blocks, protected-sleep conflicts and oversized supported fields. It retains the loaded revision and current settings.

## Scope limits

Restore merges tasks, goals, blocks, habits, notes, brain dump, journal and lesson. It does not restore every plan field, preferences, all dates, integrations or an entire account. Morning routine, completion checks, evening closeout and some review/creator fields are outside this merge path. Full-account backup/restoration remains open. The restore report previews counts, not every private text difference. Keep original exports private and preserve a pre-merge export.

## Pending acceptance

- [ ] Confirm one instance of the habit, notebook and restore panels mounts.
- [ ] Add/check habits and private notes; save/reload the selected day.
- [ ] Verify account/day changes clear private drafts and import previews, including focused fields.
- [ ] Export current day before merging. Preview a matching-day export without mutation.
- [ ] Confirm ownership and merge; no automatic cloud save. Save/reload explicitly.
- [ ] Conflicting IDs, invalid JSON, wrong dates, invalid goal/task links, schedule overlaps and protected sleep must reject without partial record mutation.
- [ ] Verify recovery, task carry-forward, routine templates and other planner tools still work.

Backlog classification: existing source implementation now explicitly wired by this batch; deployment and acceptance still open. Do not close full backup/restore. Parent records: BUILD-BACKLOG.md and LOOSE-ENDS.md.
