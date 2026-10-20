# Six learning pathways wired

2026-10-20. Static Practice this in my day links and learning-handoff.js are included on the public pathways page. The existing member entry loader already includes practice-handoff.js.

Mappings: personal-brand -> brand statement; ai-setup -> one AI prompt; content-calendar -> one post; newsletter -> first issue draft; digital-product -> product outline; website -> homepage headline.

The public page remembers only an allowlisted public pathway key in sessionStorage for 30 minutes on normal same-tab clicks. This preserves selection when member-session/login redirects omit the query. It is not a cross-device or guaranteed new-tab email handoff. Storage denial falls back to the direct link while signed in; a user may need to reopen the pathway after signing in. No journal or task content is stored in this handoff key.

Members review the task and explicitly Add. This creates unsaved work only, skips an existing unfinished practice task for the same pathway/day, and leaves scheduling and saving separate. Dismiss/Add clears the selected pathway intent. No course completion, AI disclosure, newsletter signup or publishing occurs.

Tests authored: node --test tests/learning-handoff.test.cjs. Source/mapping and intent tests do not establish live browser acceptance. Six live click-throughs, same-tab Google sign-in, storage denial, mobile layout and save/reload remain unverified.
