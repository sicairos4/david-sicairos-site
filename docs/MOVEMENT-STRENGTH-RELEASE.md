# Movement & Strength

Integrated source: public portal and two workout pages, Wellness entry, Schedule selection/blocks, actual sets/load/reps, status, private notes, rest timer and Print / Save PDF. Existing selected-day persistence is reused; valid edits remain unsaved until Save selected day. No new tables or automatic load increases.

Entry scripts preserve existing behavior and load movement.js additively. Routine intent contains only alpha/beta and expires after 30 minutes. Existing login provides sign-in/create-account. Cross-device confirmation continuation and native Google acceptance are not established here.

Original Alpha and Beta A/B/C with 3x8 exception retained. Random Wellness education links to the existing store, not unverified supplement stacks.

CI includes unit tests and Chromium public/mobile screenshots. Review the diff/checks/screenshots before approving merge. Actual Schedule integration, real-account save/reload, device behavior and deployed routes need acceptance; public-page CI does not prove those. Source committed is not deployed or accepted. Combined day PDF inclusion and training history remain upgrades. Other backlog work is unchanged.
