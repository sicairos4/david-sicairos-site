# Planner view and task-edit implementation batch

Source implementation only. No branch comparisons, tests, browser/device checks, workflow dispatch, account-data migration or deployment verification are performed for this patch. Existing automatic workflows are unchanged. No homepage, public promotion, account schema, original PDF or provider configuration is changed.

The existing entry-flow module loads planner-finishing.js through the shared Workstation module registry after its existing enhancement sequence. The new module wraps the existing timeline's view content but keeps visualDayTimeline itself visible, preserving the existing go-to-schedule target. Agenda and Timeline use the same canonical selected-day blocks; switching views changes no records or times. Agenda Edit actions locate the corresponding current block row and invoke its existing Edit button, retaining the original overlap/protected-sleep engine, time editor and schedule undo. Existing block editing was already present and is not rebuilt here.

Compact task cards keep the original task-list rows and order, so existing row-index scheduling handlers and task identities remain intact. Details reveals secondary removal/milestone controls; it does not delete or discard them. The compact choice and expanded-row choices are page-local UI state, not a new stored preference.

The task editor changes text and area only through WorkstationApp.change. It binds record, account/day context and the full task fingerprint. Optional linked-title changes require the checkbox and affect only blocks whose taskId matches and whose title still equals the old task text; times and block IDs remain unchanged. Completion, goals, practice/workout metadata and other task properties are not overwritten. Changes remain unsaved until Save selected day.

Task-edit undo is bounded to 20 edits and scoped to the loaded record/context. It checks the edited task fingerprint and any renamed block titles before restoring only text/area and those titles, never schedule times or the whole task object. It refuses stale/deleted/changed records. History is cleared on context changes, planner unavailability or pagehide. This is distinct from the existing schedule undo and is not a persistent history service.

The editor warns before relevant day/account/reload transitions discard unsubmitted edits and clears private fields when closed or context is invalidated. The implementation uses DOM text rather than task-provided HTML. New UI controls are disabled while the selected planner is unavailable. Source checks are runtime safeguards, not a claim that a test suite was run or live behavior accepted.

Still separate: Make today lighter, genuine multi-day report generation, full-account export/deletion, native binary-file sharing, missing original course PDFs, publisher runtime/account authority and original-document release workflows. This batch does not mark the full backlog complete or initiate background work.
