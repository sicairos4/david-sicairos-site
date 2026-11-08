# APP-03: section restoration

Scope: same-origin, same-tab sign-in initiated through the Workstation account-entry link. This does not implement direct login deep links, cross-device email returns, or Android cross-context storage.

Before sign-in, preserve the existing draft through the existing mechanism, then store only an allowlisted section and timestamp under a separate sessionStorage key. After a verified account has loaded and the app is not busy, consume the hint. Restore only if it is at most ten minutes old, not future-dated, structurally valid, and the destination has no explicit hash. Clear the hint on sign-out. No tokens, external URLs, or account records are stored in the navigation hint. Existing draft restore/export/discard choices remain unchanged.

No changes to OAuth destinations, Supabase redirect configuration, native callback validation, recovery, or authorization policies. Indexed native source expects the exact native-google.html destination; preserve that contract.

Validation status: source prepared only; no tests or live verification performed. Do not mark deployed or accepted merely because this file is committed.

Acceptance cases when approved: Learn > Sign in > loaded account returns to Learn; explicit destination hash wins; expired/malformed/future hints ignored and cleared; blocked sessionStorage does not block sign-in; failed login does not expose account data; sign-out clears hint; restored section never auto-imports or saves guest records.
