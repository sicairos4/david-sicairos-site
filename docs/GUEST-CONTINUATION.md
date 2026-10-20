# Guest continuation

2026-10-20. New source implementation. Prior UI handoff-only notes are superseded for this feature when the continuation scripts load.

## Flow
Guest plan -> explicit consent to unencrypted local browser storage -> Create account or Sign in -> same-origin member account -> review same selected day -> choose additions and confirm ownership/account -> stage unsaved changes -> existing Save selected day -> metadata-only database read-back confirms transfer marker -> remove temporary browser copy.

Temporary copies expire after 24 hours and are removed on a later read; no cleanup can run while the browser is closed. Avoid shared devices. Copies remain browser/origin specific; other devices or www/apex/GitHub origins require the downloaded guest JSON.

Guest snapshots include added tasks, blocks and priority only. Unadded form fields require a warning. Existing guest print/PDF controls remain unchanged. The older browser leave-page warning may also appear during continuation; canceling navigation does not remove the stored copy.

## Merge safeguards
Input normalization, limits, content-derived SHA-256 transfer ID, deterministic imported IDs, transfer marker in the same day record, preserved existing priority, skipped schedule/sleep conflicts, account/day fingerprint and explicit ownership. Guest task areas start as Other. Existing reflections, lessons, records and revision are not replaced. A full selected snapshot can only be imported once; skipped items can be recreated manually, not repeatedly merged under the same ID.

Once staged, the local copy is associated with that verified account. Changing accounts blocks further import. Adding is not saving. Failed saves retain the temporary copy. Cleanup requires signed-in identity verification before and after a filtered intentional_days read for the transfer marker. If policies/network prevent confirmation, keep the copy and offer receipt retry.

## Evidence and remaining work
Thirteen isolated assertions on the exact normalization/merge core passed before this patch was proposed. This is not a browser or production acceptance result. Repository tests are authored at tests/guest-continuation.test.cjs; no CI success is claimed.

Browser coverage still required: storage denial, expiry, downloaded-file recovery, signup/confirmation on same browser, cross-origin guidance, conflicting day and priority, ownership, rapid double click, existing unsaved edits, server revision conflict, save failure, receipt retry, account change, deletion and print. No SMTP, auth policy, database migration, APK or Muse configuration is changed.
