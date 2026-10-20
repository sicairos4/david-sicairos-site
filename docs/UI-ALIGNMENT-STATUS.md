# UI alignment and remaining work

2026-10-20. Source batch; no executed CI or live visual acceptance is asserted.

## This batch
- Shared toolbar rewritten with an actual 44px square 209 mark, no wrapping desktop groups, compact menu through 1200px, measured overlay offset, hidden/inert closed menu, visible-only keyboard focus trap, Escape/close action and synchronized group aria state.
- One visible shared theme control; duplicate member header theme/public controls are hidden by toolbar-scoped CSS. Home, Workspace and Guest remain in the mobile menu.
- Shared ui-polish.css loaded by topbar.js: consistent action padding, 44px target height for scoped controls, form sizing, mobile 16px inputs, flex wrapping and focus states. Compact timeline gesture handles are intentionally excluded.
- Existing navigation destinations preserved except 209 Connect Studio display label simplified to 209 Connect. Legacy aura.html resource destinations are not silently replaced or claimed retired.
- Responsive audit authored for 10 pages at 320, 390, 768 and 1280px, with screenshots, overflow, mobile-menu, square-logo and scoped target checks. No account or database writes.

## Scope limits
Pages using topbar.js receive the shared sheet. Guest planner remains independently themed by simple-day.css. Static pages without the shared toolbar need separate stylesheet/link review. No claim that every route is audited. Offline preview can show expected unavailable-service states. Human screenshot review and actual signed-in/device acceptance remain required.

## Remaining backlog
- Guest-plan temporary-copy consent, direct signup mode, post-login import review, conflict-safe merge and cleanup after confirmed save. Current guest flow is a protected handoff, not transfer.
- Supabase signup/SMTP/backend password policy and real confirmation/recovery delivery.
- Save-state consistency, day switching, account isolation and full backup/restore.
- Android build/install/signing and device layout acceptance.
- Full site route inventory, forms, checkout/access delivery, learning resources, printable outputs and legacy resource reconciliation.
- Real Public Files collection/provenance and publishing acceptance.
- Muse runtime connection, scoped MCP health/status, approval queue and execution receipts.

The prior pending task-schedule browser workflow was not approved/committed. This batch adds responsive audit only and does not imply those interaction tests ran.
