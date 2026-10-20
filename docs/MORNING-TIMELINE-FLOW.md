# Morning → daily timeline handoff

Scope: connect the existing morning routine to the existing day scheduler, not implement the pending calendar drag/resize maker or newsletter integration.

Changes: keep day-planning fields visible; hide the old gate checkbox; show scheduled day cards beneath the morning preview; distinguish previews from actual blocks; rename the add action; after successful atomic addMany, open Schedule and focus the block list; synchronize on the application render event and loaded record/context rather than parsing status message text; retain duplicate/draft/context guards and explicit Save selected day. Failed routine edits restore the local steps array.

Scheduled cards are a read-only chronological summary, not proportional draggable calendar blocks. Existing scheduler handles overlap/sleep validation and undo.

Acceptance pending, not claimed run:
- [ ] Add enabled morning steps; see matching day/date/times in Schedule immediately.
- [ ] Return to Morning; daily cards match the current record.
- [ ] Day-planning fields stay visible after account/day reload.
- [ ] Duplicate morning blocks, overlaps, protected sleep, changed contexts and unfinished block drafts reject without partial additions.
- [ ] Cancel confirmation changes no blocks.
- [ ] Undo, explicit save and reload preserve their existing behavior.
- [ ] Day/account switching shows no previous-day summary while loading.
- [ ] Touch/keyboard routine reorder alternatives still work.
