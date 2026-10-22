# Saved-range PDF report

## Source implementation scope

Adds assets/workstation/range-report.js through the existing review-share.js module loader. The report is read-only and uses the existing authenticated account client and browser-safe Supabase publishable configuration. No service-role credential is introduced.

The Review fieldset supports an inclusive 1–31 calendar-day range, defaulting to seven days ending on the selected day. Only saved intentional_days records for the authenticated user are requested. Unsaved edits are excluded. Missing dates say No saved record returned, not failed days.

Task counts always appear. Task details and time blocks are selectable. Journal, lesson, weekly review and evening closeout are individually opt-in and trigger a private-data confirmation before reading. The plan column is retrieved for tasks and blocks and may contain private plan fields; only selected sections are projected into the preview. Journal and lesson columns are requested only when selected. This is not a database-wide atomic snapshot or full-account backup.

## Safeguards in source

- Session and user validation using the existing account client.
- User and date filters; limit 32 to detect an unexpected oversized result.
- Four-million-byte streaming response cap; unsupported bounded-stream browsers stop instead of falling back to an unbounded read.
- Strict dates, duplicate/range checks, saved plan/task/block validation and per-day item caps.
- Task and writing content rendered with textContent, not user-provided HTML.
- Abort loading, stale-result rejection and preview cleanup on observed account/day/record transitions and pagehide.
- Shared preview collision guard, background inert restoration, keyboard focus containment, Escape dismissal and focus return.
- Existing native print URI and browser Print / Save PDF; no new routine text/JSON report output.
- Printing does not claim file-save or delivery success.

## Preserved behavior and exclusions

Existing review sharing behavior remains unchanged apart from loading the new module. The new report does not add text sharing. Existing saved-day recovery is separate and is not changed. No tasks, schedules, account records, credentials, payment configuration, published documents, social posts or Android signing identities are modified.

## Status and deferred acceptance

This document describes implementation intent and source safeguards, not evidence of runtime acceptance. No tests, browser/device checks, deployment checks, branch comparisons or workflow dispatch are included in this batch. Existing push-triggered automation, if any, is not disabled or verified.

Deferred acceptance includes actual module loading in the application shell, existing real-record compatibility, rapid account transitions, keyboard and assistive-technology behavior, browser PDF layout, native WebView printing and print-dialog lifecycle. Keep source committed, compiled, deployed, artifact produced, installed and accepted as distinct states.

This batch does not complete workload deferral/rescheduling, broader account export/deletion, optional Drive backup, course asset recovery, durable public-record ingestion, publishing activation or Android release activation.
