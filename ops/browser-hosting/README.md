# Browser host deployment extension
Prepared 2026-11-08. Source only; not deployed. No test suites or live platform requests run to produce these files.

## Targets
Run Chromium locally on a selected owner-controlled Linux host. A cloud VM can be that local execution host; it is distinct from this chat's offline Python environment. DigitalOcean authentication was requested but no server was selected, created, or charged. No remote execution connection exists in this deployment record. The fallback is a second owner-controlled Linux host, initially standby. targets.example.json is a template, not a registered host.

## Install on the selected host
This extension requires the previous 27-file browser source package. Transfer it privately and locate its 04_Automation directory. Copy this extension alongside it. On Debian/Ubuntu Linux, as an administrator:
```
sudo bash install-host.sh /absolute/path/to/209-social-media/04_Automation
```
The installer downloads Python dependencies and Chromium on that machine, creates the browser209 service user, installs private state directories and service/timer definitions. It does NOT apply database migrations, create login sessions, enable the timer, start a worker, provision cloud servers, or change existing cron jobs. No passwords are included. It copies only named source files, not arbitrary local secrets.

Configure /etc/209-browser/worker.env privately, including a scoped TLS-verified BROWSER_DATABASE_URL; never commit that file. Use a migration-only connection separately to apply the reviewed browser schema, then install the role-specific RLS policy and grants. The prior browser schema defaults to denying ordinary runtime access; do not bypass it with a service-role credential.

Configure /etc/209-browser/accounts.json with resolved identities and provider-owned allowlists. All examples remain disabled until configured. Perform the first login in a visible desktop session as browser209 using the same environment/state paths. A headless server needs an owner-authorized private desktop arrangement; none is installed here. Do not expose a browser debug port, VNC, or cookies publicly. Never disable Chromium sandboxing to hide a host incompatibility.

After an exact task is authorized and runtime prerequisites have been satisfied, an administrator can start one execution with `systemctl start 209-browser.service`. Recurring consumption additionally requires the existing authoritative publishing-ledger integration, account caps/quiet hours, revocation handling, and receipt reconciliation; these remain unfinished. Only then may the owner set BROWSER_WORKER_ROLE=primary and enable 209-browser.timer. The timer is a host consumer, not a replacement for the existing independent-publisher-209-minute cron job. Do not dispatch one publication into both routes.

## Fallback
Install the same source revision on another selected host with BROWSER_WORKER_ROLE=standby. Keep its timer disabled. This is a standby policy, not working automatic failover. Before promotion, stop the primary, reconcile running/uncertain jobs against external effects, and establish the authorized account profile on the fallback. Copying a live Chromium profile across hosts is not a safe failover procedure. The existing source has host-local profile locks and per-job database claims, not a cross-host per-account lease. Automatic promotion is therefore deliberately not implemented. No browser state should be stored in shared Drive or the repository.

## Current boundaries
The browser staging queue is not linked to ai_coordination authorizations. The v2 Muse worker endpoint currently permits health.snapshot and queue.summary only. Neither this installer nor a connected cloud account expands that contract. Facebook permissions, account identity, and successful publication remain unresolved. No source, template, or enabled scheduler is proof of a running browser or a public post.
