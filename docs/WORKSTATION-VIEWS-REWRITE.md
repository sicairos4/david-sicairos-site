# Workstation base-view rewrite

2026-10-20. Rewrites members/app.html rather than adding another DOM-rearrangement module. Adds a statically linked, scoped views.css.

Copy and hierarchy: concise Workstation introduction; eight visible navigation destinations; legacy Tasks/Schedule sections retained for existing routing/consolidation; shorter morning, task, schedule, milestone, focus, reflection, review and creator labels; three practical learning resource cards. Large above-app legal introduction moves to a named footer disclosure; About/Privacy/Terms links remain in the gate and footer.

Compatibility: original input IDs, data-bind paths, data-routine keys, limits, form IDs, account/demo controls and deferred script order remain. The original task-area option values remain for existing normalization code. Existing entry-flow, simple-day, reflection and page-cleanup modules are retained, not claimed replaced; they still own some final headings and grouping. No new loader, authentication behavior, autosave, migration, AI call or publishing action is introduced.

Scope: base member views and their scoped styling. Public website redesign, Form 700 intake/upload/library work, shared-bootstrap replacement, account acceptance and native release work are not completed by this commit. No browser or deployed acceptance pass is asserted.
