# Today control consolidation

2026-10-20. Source implementation; no rendered or live-account pass is asserted.

Keep: one task entry form, existing morning and habit check-ins, one compact schedule preview showing up to six blocks, one main schedule opener and explicit Save. Full time-block editing/undo and task-specific scheduling remain available in expandable tools.

Relocate: Quick capture to Reflection in reflection-only mode; account/demo tools to Settings; small-start helpers under one optional disclosure; the independent daily review checklist to Reflection; schedule notes under Day notes. Existing handlers and data fields stay mounted so saving and exports remain compatible.

Remove duplicate presentation: the base plannerOverview is hidden; simpleDaySummary and repeated permanent introductory/help paragraphs are no longer created; redundant Plan time/Choose tasks/Focus links are removed from dayOptions; the extra View timeline button is removed after its module loads. No saved tasks, habits, check-ins or schedule blocks are deleted or merged.

Guest import stays on Today only while a temporary copy exists; otherwise it is available in Settings. Legacy #tasks/#schedule links route into Today. A task and a to-do are the same concept, habits remain repeatable check-ins and blocks reserve time.

Tests cover schedule-summary computation and source wiring, not actual browser usability. Mobile layout, keyboard focus, reflection capture, existing unsaved edits, morning transfer, guest restore and day switching require browser acceptance. No new API connection or secret is required.
