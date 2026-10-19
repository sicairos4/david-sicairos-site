# Saved weekly progress

Extends the existing Review screen and replaces its saved-task-only load handler. Loads the seven calendar day keys ending on the selected day and the preceding seven through ConnectCore.Cloud.review with identity checks around requests. No journal/lesson columns are selected, and unsaved edits are not included.

Shows saved-day coverage, completed/total task entries, done/partial/skipped/unrecorded habit entries, day-scoped milestone attainment using the existing manual-plus-linked-task convention, and scheduled block minutes. Planned time is not tracked work. Counts are day entries, not unique people, habits, tasks or cross-day milestones. Missing rows are not failed days; 0/0 is not a completion percentage. Malformed entries are excluded and counted. Older days without habit arrays do not establish habit adherence.

A user can append the exact summary to the existing private weekly review draft, then explicitly Save selected day. No new table, scheduler, AI request, publishing action, background job or automatic account write is added. Private progress and stale requests are invalidated when loaded day/record/account context changes or the page is left.

Source authored without running tests, live-account verification, deployment checks or APK compilation.
