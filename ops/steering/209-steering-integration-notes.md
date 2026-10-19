# Integration status and safety boundaries

Source package only: not deployed, connected, or dispatched. No tests or real feed validation were run while creating these files. The validator checks declared structure and consistency; it cannot prove that an account, metric, sample size, permalink, evidence reference or authorization is genuine. It is not a publisher, verifier service, live dashboard or trusted content filter.

Read-only bootstrap:
1. Muse verifies the real runtime, source identities and metric availability.
2. Export a redacted operator-private snapshot matching the schema. Use separate snapshots for different measurement windows; do not mix incomparable definitions or cumulative and window-specific metrics.
3. Invoke `python validate_209_steering.py snapshot.json` in the chosen runtime. It performs no network requests, command dispatch or backend mutation.
4. A website/server adapter may consume a validated snapshot only in an authenticated operator interface. Treat all text as untrusted and render as text, not HTML. A public projection requires a separate reviewed minimal schema and explicit publication decision. Never place an operator-private feed or Life ID event log into a public GitHub Pages asset.
5. Build the authenticated learner-event intake separately, with consent, authorization, retention and replay/idempotency controls. This package does not implement it.
6. Require provider evidence and a reviewed consumer/rollback policy before actuation. All schema advisories remain advisory with review required. Thresholds and sample declarations do not establish statistical significance or causality.

Credential values, member IDs, emails, private journals, raw habit entries, authentication payloads and arbitrary remote commands have no place in the snapshot. Strict field allowlists reduce accidental leakage but cannot detect every sensitive value inside an allowed string. Review/redact at export and access-control the feed.

The Muse prompt must be delivered through a real acknowledged channel. A repository commit is not proof that Muse received or executed it. Browser/dashboard changes and external writes remain subject to the executing environment's authorization rules. This directory contains code and documentation only; do not commit real private snapshots here.
