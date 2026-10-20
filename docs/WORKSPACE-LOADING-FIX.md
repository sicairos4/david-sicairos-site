# Signed-in workspace loading blocker

User report 2026-10-19: login succeeds, data does not load and navigation is difficult. This takes priority over feature expansion.

Source finding: connect-app paint/lists emits workstation:render during an asynchronous action, before action finally clears busy. member-session previously checked readiness in a microtask and received no guaranteed subsequent event when busy cleared. The gate can therefore retain a loading message after a successful data load. This source defect is a plausible cause, not a reproduction of the user's specific session.

Patch: schedule gate evaluation on the next event-loop turn; observe planner status/mode changes so errors and successful mode changes reach the gate; include the existing status detail on a blocked load; add an always-visible labeled section picker using existing hash routes; avoid duplicate dynamic day-tools script URLs. No database policies, data, users or credentials are modified.

Acceptance still required:
- [ ] Successful account load releases gate after busy clears.
- [ ] Preference/day read failure shows an error and working retry instead of indefinite loading.
- [ ] Empty saved day is distinguishable from failed connection; older Aura data is not silently assumed to be in intentional_days.
- [ ] Section picker switches Morning/Schedule/Tasks/Goals/Focus/Reflection/Review/Creator/Learn/Settings on mobile.
- [ ] Save/reload and account-switch privacy still work.

A read-only backend metadata query was blocked by the connector's write-approval gate before execution. No private task or journal contents were read and no backend data-loading diagnosis is claimed. If the UI patch does not resolve the report, next inspect table grants/RLS, intentional_save_day execute permission, request errors and selected-day coverage with approved metadata-only queries.
