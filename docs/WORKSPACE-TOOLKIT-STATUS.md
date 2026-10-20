# Workstation toolkit and simplified Today

2026-10-20. Database migration workspace_toolkit_and_transactional_backup succeeded before this commit. The user approved source integration and a simpler member experience. Neither source nor migration proves live recovery or installed mobile acceptance.

- One visible explanation: task/to-do = one action to finish; habit = a repeated check-in; schedule block = time set aside. Optional habit-to-task conversion remains optional.
- Today shows a compact day-as-built list with up to eight upcoming blocks and an expandable full-day planner. Existing morning/habit/task modules and explicit Save remain. Older category values remain on existing saved tasks.
- Account-owned repeat rules and reusable task lists require manual preview/add on each day. Nothing schedules or repeats in the background. In-app carry-forward reads one earlier saved day and copies selected unfinished tasks without changing the source day.
- Backup exports saved planner days, reflections, preferences, digests and toolkit as unencrypted JSON. It excludes passwords, identity/profile metadata and browser-only drafts. Restore skips existing days, does not automatically enable reminders, and requires owner match and explicit confirmation. No existing account was exported or restored by this commit.
- Six public learning pathways link to an optional task preview in Today. Task add, scheduling and saving remain separate actions; no AI sharing or publishing.

Acceptance still open: toolkit RLS and real-account writes, competing-tab conflicts, in-app carry-forward, same-account backup download and missing-day restore with a nonproduction account, study-task redirect and mobile display. The server-side restore supports revision-checked replacement but the user interface intentionally does not offer it. Accounts larger than 25 MB need paginated backup work. Email SMTP, installed Android release, Muse runtime and wider site backlog remain separate.
