# Deliberate task carry-forward

Implementation: private earlier-day export -> explicit task selection -> ownership confirmation -> copy into loaded day as unsaved edits -> existing Save selected day. No automatic cloud lookup, rollover, background write, task deletion or full backup restoration.

Only unfinished task text/area and source identifiers are copied. Original goal links are cleared; new task IDs are generated. Existing source provenance or matching text/area prevents duplicates. Journal, reflection, schedule and completed tasks are not copied. The selected file stays local; its preview is not uploaded. User ownership is an explicit attestation, not cryptographic verification of an export.

Pending acceptance (not claimed run):
- [ ] Export an earlier day; preview with no mutation.
- [ ] Copy selected unfinished tasks only, then save/reload.
- [ ] Original day remains unchanged.
- [ ] Repeated import skips duplicates.
- [ ] Reject same/future source day, invalid JSON, invalid tasks, and files above size cap.
- [ ] Reject stale preview after day/account or loaded-record replacement.
- [ ] Cancel/clear makes no mutation.
- [ ] No journal text, milestone links or completed tasks appear in copied records.

## Backlog progress

- Source-only: duplicate morning guards (a6ecc4c), morning completion/evening closeout (f7faa5c), month navigation/routine templates (76cf93f), template refresh wiring (87ffffc), and this file-based carry-forward batch. Browser/save/reload acceptance remains open.
- Public Files: eight tables deployed with RLS; database browser source committed. Real filings, document storage, controlled intake and end-to-end tests remain open.
- Android: branded 0.3.3 source committed; build/artifact/install/signing acceptance remains open.
- Still open: full backup/restore, saved-record monthly overview, session/private-field clearing, store/learning/media delivery, Muse/runtime/publisher integrations, monitoring/restore and other items in BUILD-BACKLOG.md and LOOSE-ENDS.md.
