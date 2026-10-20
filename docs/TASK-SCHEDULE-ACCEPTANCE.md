# Task-to-schedule flow

Updated 2026-10-20. Source implementation; no live/browser acceptance is asserted.

## Implemented by this batch
- Intercept Schedule on an existing task and show its title with start time, duration, preset durations and calculated end time.
- Keep the preview separate from the account record until Add to day.
- Submit through the existing block form to retain scheduler overlap/sleep validation, task linking and schedule undo. No direct backend writes or autosave are added.
- Clear the scheduling preview on loaded day/account/record changes; confirm before replacing an existing scheduling draft.
- Route View timeline to the timeline regardless of block-title draft text. Choose a task to schedule navigates to tasks, not an empty block editor.
- Add linked-task information and Start focus in the existing detailed block list. It selects the task and opens Focus; the timer still starts explicitly. Completion remains a separate action.
- Preserve existing drag/resize, exact-time edit, protected sleep and undo. No animation, general task undo, full backup/restore or Muse execution is added.

## Tests
Run node --test tests/task-schedule-flow.test.cjs. These tests cover draft calculation, non-mutation, stale-task/input rejection and source integration guards. They do not prove rendered behavior.

## Browser acceptance still required
- Schedule a real task, cancel, add and save/reload; confirm task link persists.
- Reject overlaps and protected sleep with no unintended block.
- Check View timeline with a filled block draft; it must not open the editor.
- Check direct Tasks/Schedule links, browser Back and keyboard focus.
- Verify Edit opens the details panel and preserves the task link.
- Verify focus selection respects an existing running timer and never marks completion automatically.
- Verify scheduling draft invalidation on account/day changes and after save/reload.
- Verify mobile stacking, touch targets, keyboard, move/resize and undo.
- Test when the enhancement fails to load: existing block editor remains available.

The linked-task focus action is in the detailed block list, not overlaid on small timeline cards. Live deployment, account isolation and APK acceptance remain separate.
