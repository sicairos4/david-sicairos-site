# Morning transfer acceptance

Implementation prepared 2026-10-19. Parent running list: BUILD-BACKLOG.md.

This patch adds explicit rejection when any proposed morning block exactly matches an existing title/start/end, checks again after confirmation, and rejects a changed account/day context. It does not silently delete or replace existing blocks. Existing scheduler collision and sleep protection remain authoritative.

Not yet browser-tested; source commit is not acceptance.

- [ ] Empty selected day: add the morning once; all blocks appear as unsaved changes.
- [ ] Repeat without saving: reject with a clear message; block count unchanged.
- [ ] Save/reload then repeat: reject; count unchanged.
- [ ] One exact matching step: reject the entire transfer, not only that step.
- [ ] Different selected day: allow when no collision/protected sleep conflict exists.
- [ ] Changed day/account around confirmation: reject.
- [ ] Changed titles/times: existing scheduler still rejects overlaps and protected sleep.
- [ ] Cancel confirmation: no mutation.
- [ ] Sign out/switch accounts: no old record modification.

No morning completion, carry-forward, evening closeout, APK installation or other backlog item is claimed complete by this patch.
