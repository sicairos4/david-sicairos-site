# Toolkit completion pass

2026-10-20. Source implementation only; no backup or restore of real account data is performed by this commit.

Completed in source: reusable-list rename/removal, repeat-rule removal, matching-day manual addition, explicit copy of unfinished tasks, account/context verification before and after async operations, private preview clearing, checked file-read sequencing, optional preference restore and revision-checked toolkit-definition restore.

Default restore skips existing saved days and keeps preferences/definitions unchanged. Optional preferences restore turns private digests OFF. Optional toolkit restore replaces definitions, not tasks already stored in saved days. User must choose options before selecting a file, review and explicitly confirm the operation. Large backup pagination, profile/identity export and replacement of existing days are outside this interface.

This does not implement background recurring-task generation, push/email reminders, Google Calendar sync, automatic publishing, account deletion, Android production signing, Muse runtime connectivity, store checkout fulfillment or real Public Files collection. Those remain tracked, not marked complete.

New workflow runs existing toolkit/learning tests plus source-wiring assertions. A passing wiring assertion is not a production recovery test. Workflow result and live UI/account behavior are not asserted here.
