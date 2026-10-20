# Daily flow implementation and acceptance

Batch: morning completion and evening closeout. Parent backlog: docs/BUILD-BACKLOG.md.

The Morning view adds enabled-step checkboxes, keyed by stable routine step ID inside plan.morningStepChecks. The Review view adds helped/change/next-step reflections and a reversible closedAt marker in plan.eveningCloseout. Both use WorkstationApp.change and the existing Save selected day mechanism. No automatic save, publication, task carry-forward or deletion occurs. Closing a day is not an edit lock. No database migration is needed because the existing record normalization preserves plan fields.

Source prepared; not yet runtime-tested or marked accepted.

- [ ] Confirm script loads and both panels appear once.
- [ ] Toggle morning steps, Save selected day, reload, verify checks persist.
- [ ] Reorder/rename routine steps; stable IDs retain checks. Disabled steps leave the active count.
- [ ] Day/account switch resets displayed state without copying private reflections.
- [ ] Enter closeout, close, save, reload and reopen; state persists correctly.
- [ ] Closeout does not move tasks or expose text to public records, publishing or sharing.
- [ ] Busy/loading and stale-context edits are rejected.
- [ ] Recovery, account isolation and normal scheduler behavior remain intact.

Remaining separate work: monthly navigation, templates, explicit carry-forward, selected-task continuity, full backup/restore, real APK delivery/install/signing, Public Files real-record collection, and other backlog items.
