# Reflection cleanup

2026-10-20. Source layout change; live/browser acceptance is not asserted.

Default: Reflection heading, one privacy explanation, selected-day label and existing main journal field. Optional: four guided prompts; separate brain dump and existing private notebook; quick capture that appends to main journal; generalized lesson; independent daily-review checklist. Evening closeout stays in Review.

This re-parents existing labels, textareas, fieldsets and forms. Values, data-bind paths, maxlength limits, private-note handlers, main save bar and creator-copy behavior are not changed. No journal fields are merged, erased, uploaded to AI or automatically published. The brain dump remains plan.brainDump and free writing remains journal.

Member loader adds reflection-layout.js/CSS after the simpler Today loader. Child insertion observation handles the notebook loading later without replacing its form. No new API or secret is needed. Source regression checks do not prove rendered display, late loading, keyboard focus, draft clearing, save/reload or print output. Those remain browser acceptance items.
