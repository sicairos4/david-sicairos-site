# 209 steering source package

This directory contains source and documentation, not private operational data. GitHub Pages or a public repository can expose files here; an operator_private field is not access control. Never add real snapshots, member events, passwords, tokens or data-filled dashboards to this checkout. Ignore patterns are only a precaution, not a security boundary.

## Local operator dashboard

The renderer consumes the existing v1 schema and validator, performs no network calls, and writes a local HTML report. It does not collect analytics, run a server, connect to Muse, publish content, execute advisories or authorize anything. An existing runtime must first export a genuine sanitized snapshot.

Use Python 3.9 or newer with IANA timezone data available. From the website checkout:

```sh
python ops/steering/validate_209_steering.py /path/outside-the-repository/snapshot.json
python ops/steering/render_209_steering.py /path/outside-the-repository/snapshot.json
```

The default report is dashboard.html inside the current operator's ~/.local/share/209-steering directory. Open that local file in a browser. Use --output to choose another path outside the repository, and --max-rows from 1 to 1000 to change the displayed observation limit. The renderer refuses inputs or outputs inside this website checkout. Do not put reports into another public checkout or synced/public folder either.

The report includes source availability, measurement-window and expiry labels, reported metrics and publication states, declared evidence references, local row filtering and advisory reasons. It does not infer unique users, causal attribution or platform comparability. Missing metrics remain Not reported. Expired/malformed snapshots are refused at generation; the HTML also marks the whole report expired after its declared maximum age while open. Advisory-specific expiry is displayed separately. No browser fetches or command controls are included.

Generated files use owner-only permissions on systems supporting POSIX modes. An existing older report is not deleted if a later generation fails; always inspect its generation and expiry labels. Permissions and CSP do not protect against a compromised device, privileged local software, browser extensions or deliberate copying. The validator does not independently verify claims or detect every sensitive string.

## Coordination

Read 209-muse-collaboration-prompt.md and 209-steering-integration-notes.md. Muse must acknowledge actual runtime/export access and provide redacted evidence. The authenticated event intake, production/private dashboard hosting, consent model and existing-publisher consumer integration remain separate tasks. No unattended execution is enabled by this package.

This renderer was authored as source; no real data run, browser acceptance or live runtime connection is claimed.
