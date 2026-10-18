# Workstation Block 1: new isolated source build

This is a newly authored implementation, not recovery of an earlier ZIP or a claim that prior staging tests passed.

## Source manifest
- assets/workstation/core.js: memory-only same-day schedule state, validated additions, opening selection, invalidation and defensive copies.
- assets/workstation-free-time.js: existing finder dependency, unchanged. Its legacy DOM adapter does not mount because staging has no gapForm element.
- members/workstation-staging.html: isolated form-based UI, one controller, no existing planner controller or account SDK.
- tests/workstation-shared-core.test.cjs: eight new unit tests.
- tests/workstation-free-time.test.cjs: existing finder tests, unchanged.

## Verification required before merge
Run: node --test tests/workstation-shared-core.test.cjs tests/workstation-free-time.test.cjs
These tests have not been executed as part of authoring this commit. Browser acceptance is also pending: keyboard navigation, mobile layout, selection without automatic insertion, invalidation after settings/day/schedule changes, adjacency, overlap rejection, and reload clearing.

Serve the repository through a local HTTP server and open members/workstation-staging.html. It loads only repository-local scripts.

## Boundaries
No changes to members/app.html, member data, auth, database, tracker, Signal, subscriptions, or Android. No persistent save, task links, sleep protection, drag/resize, undo, multi-day retention, timezone conversion or external calendar reads. Changing day explicitly discards current memory blocks after confirmation; closing/reloading loses them. Suggestions can include earlier times and show earliest starts in at most eight gaps.

Do not merge on the assumption this completes account-backed planner integration. The branch commit establishes a reviewable source candidate; account integration and acceptance testing remain separate release blockers.
