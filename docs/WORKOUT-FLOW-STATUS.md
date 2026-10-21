# Workout flow wiring

The approved flow module is now wired into the toolbar, workout pages, account/guest pages, Wellness, Workstation and University entry. The new lesson and stylesheet are included.

The workflow runs source/unit checks and a Chromium toolbar-to-guest task/scheduling smoke test. The browser test source was syntax-checked locally, not executed locally. Production account save/reload, native/mobile acceptance, review, merge and deployed URLs remain separate gates. No automatic block, task completion, recurrence or private guest-plan transfer is introduced.
