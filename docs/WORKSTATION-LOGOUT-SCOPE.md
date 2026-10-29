# Workstation logout scope

This source batch routes the planner and profile sign-out controls through one action, restores the shared account client, and requests Supabase sign-out with local scope. It is intended to sign out this browser/WebView session, not all devices or the user's Google account.

Unsaved planner edits require confirmation before sign-out. A signed-out user's current tab work is not cleared merely by attempting to sign out. Confirmed sign-out clears the planner through its existing wipe function and clears the preserved pre-sign-in session-storage copy. The tool remains accessible afterward.

Profile controls retain their own unsaved-profile confirmation before calling the shared action. Sign-out controls are hidden when the runner reports no account/session identity. Account calls have a timeout; a timeout is not a successful sign-out receipt and a late auth event can still arrive. No saved account rows are deleted.

This batch does not audit or modify every other authentication screen. It does not change Google provider settings, revoke all devices, clear all browser storage, or claim live acceptance. No tests or live authentication requests are performed by the implementation workflow. The APK still loads hosted website content; source merge and deployment remain separate from artifact compilation and device installation.
