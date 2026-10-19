# Day tools implementation

Daily habits, private brain dump and notebook notes mount inside the existing Morning and Reflection views. All record mutations use WorkstationApp.change and the existing explicit selected-day save/RPC. No AI, publishing, new database table, automatic upload, local-storage persistence or background execution is added.

Restore previews version 1 JSON exports under 1 MB and requires a matching selected day and ownership confirmation. Supported arrays merge by ID; differing entries with the same ID block the merge. Current priority, routine/sleep settings, revision and unknown plan fields are retained. Reflections, lessons and brain dump append within length limits. The current editor imposes a 200 KB compact-JSON plan limit before backend validation. This is supported-entry merge, not a complete full-account restore or cross-day sync.

Unadded note drafts and restore previews clear when the loaded record/context changes. File content remains in browser memory until the user explicitly merges and subsequently chooses Save selected day. Existing day exports include the new plan fields. Credentials and protected API access remain separate release blockers.

Source authored only. No tests, deployment inspection, APK compilation, browser acceptance or live account save was performed as part of preparing this change.
