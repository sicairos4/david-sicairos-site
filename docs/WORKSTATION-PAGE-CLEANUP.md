# Consolidated Workstation page cleanup

2026-10-20. Scope: member application views, not all public website pages, APK installation, auth migration or the shared-bootstrap replacement.

Creator: retain draft, reviewed-lesson import and copy/download; add optional static writing prompts; hide one duplicate publishing notice; improve clipboard-unavailable handling and prevent repeated copy clicks while pending.
Review: daily closeout stays visible; weekly summary, draft, guided form, progress and exports move together into a weekly disclosure. Guided questions default closed once per mount. No fields are merged.
Settings: group profile/account, preferences, password access, exports/backup, connection status and advanced demo/account tools. Existing nodes and handlers remain mounted, including late-loaded panels. Unknown controls are not removed.
Goals becomes Milestones in visible navigation and heading; no route or record schema change. Focus keeps timer/link controls first and moves explanatory paragraphs into optional help. Learn explains existing destinations. Shared CSS applies spacing, wrapping, focus indicators, mobile text sizing and reduced motion to member views only.

The general page cleanup currently loads from the existing creator-output module, avoiding another edit to the shared loader. Moving this dependency to a dedicated application bootstrap remains architectural debt, not completed by this visual pass.

Five local Node tests passed for syntax, source contracts and draft snapshot logic. These are not DOM/browser, authentication, save/reload, two-account, print, native clipboard/download or accessibility acceptance. Existing creator tests remain in CI; hosted CI/deployment/browser results require verification. Explicit saves, original field limits, consent, revision checks and restore confirmations are unchanged. No new API key, service authorization, automatic publishing or saved-data migration is introduced.
