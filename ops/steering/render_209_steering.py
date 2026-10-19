import argparse
import base64
import datetime as dt
import hashlib
import html
import json
import os
from pathlib import Path
import tempfile

from validate_209_steering import check, timestamp, InvalidSnapshot

REPOSITORY = Path(__file__).resolve().parents[2]
SCRIPT = """(()=>{'use strict';const search=document.getElementById('search'),rows=[...document.querySelectorAll('[data-observation]')],count=document.getElementById('visibleCount');function filter(){const term=search.value.toLowerCase();let visible=0;for(const row of rows){row.hidden=!row.textContent.toLowerCase().includes(term);if(!row.hidden)visible++;}count.textContent=visible+' displayed rows match';}search.addEventListener('input',filter);filter();const state=document.getElementById('freshness');const until=Date.parse(state.dataset.until);function tick(){const expired=Date.now()>=until;state.textContent=expired?'EXPIRED SNAPSHOT — reload from a fresh export before considering any advisory.':'Static snapshot: inside its declared age limit. This is not a live health check.';state.classList.toggle('expired',expired);for(const box of document.querySelectorAll('[data-advisory]'))box.classList.toggle('expired',expired);}tick();setInterval(tick,1000);})();"""
STYLE = """body{font:16px system-ui,sans-serif;line-height:1.5;background:#f3f1e7;color:#183e30;margin:0}main{max-width:1280px;margin:auto;padding:24px}h1{letter-spacing:-.03em}.panel{background:white;border:1px solid #cad5cc;border-radius:14px;padding:18px;margin:16px 0}.badge{display:inline-block;padding:5px 10px;border-radius:99px;background:#174b37;color:#f3f1e7}.notice{border-left:5px solid #b99856;padding:12px;background:#fff}.expired{border-color:#9c302d!important;background:#fff1ed!important;color:#6b211e}table{border-collapse:collapse;width:100%;min-width:900px}td,th{padding:10px;text-align:left;border-bottom:1px solid #d6ddd6;vertical-align:top}caption{text-align:left;font-weight:700;padding-bottom:12px}.scroll{overflow-x:auto}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit}input{box-sizing:border-box;width:100%;font:inherit;padding:12px;margin-top:6px;border:1px solid #cad5cc;border-radius:8px}dt{font-weight:700}dd{margin:0 0 12px;overflow-wrap:anywhere}[hidden]{display:none!important}:focus-visible{outline:3px solid #175c42;outline-offset:3px}@media(max-width:600px){main{padding:14px}.panel{padding:14px}}"""

def escape(value):
    return html.escape(str(value), quote=True)

def cell(value):
    return '<td>' + escape('Not reported' if value is None else value) + '</td>'

def interaction_ratio(metrics, availability):
    parts = [metrics[key] for key in ['likes', 'replies', 'shares', 'saves']]
    views = metrics['views']
    if availability != 'available' or views is None or views == 0 or any(value is None for value in parts):
        return 'Not comparable'
    return format(100 * sum(parts) / views, '.2f') + '% reported interactions / views'

def document(snapshot, checked_at, maximum):
    sources = {source['id']: source for source in snapshot['sources']}
    expires = timestamp(snapshot['generated_at']) + dt.timedelta(seconds=snapshot['max_age_seconds'])
    script_hash = base64.b64encode(hashlib.sha256(SCRIPT.encode()).digest()).decode()
    policy = "default-src 'none'; style-src 'unsafe-inline'; script-src 'sha256-" + script_hash + "'; connect-src 'none'; img-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'"
    parts = ['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="referrer" content="no-referrer"><meta http-equiv="Content-Security-Policy" content="' + escape(policy) + '"><title>209. operator steering snapshot</title><style>' + STYLE + '</style></head><body><main><p class="badge">209. / OPERATOR-PRIVATE / ADVISORY ONLY</p><h1>Steering snapshot</h1>']
    parts.append('<p class="notice">Local static report. No external requests, publisher controls, automatic decisions, or member-journal analysis. Declared evidence and metrics have not been independently verified.</p>')
    parts.append('<section class="panel"><h2>Snapshot and freshness</h2><dl>')
    for label, value in [('Snapshot ID', snapshot['snapshot_id']), ('Generated', snapshot['generated_at']), ('Structure checked at UTC', checked_at.isoformat()), ('Declared expiry UTC', expires.isoformat()), ('Measurement window', snapshot['window']['start'] + ' through ' + snapshot['window']['end']), ('Window timezone', snapshot['window']['timezone'])]:
        parts.append('<dt>' + escape(label) + '</dt><dd>' + escape(value) + '</dd>')
    parts.append('</dl><p id="freshness" role="status" aria-live="polite" data-until="' + escape(expires.isoformat()) + '">Static snapshot. Do not use after its declared expiry.</p></section>')
    parts.append('<section class="panel"><h2>Source availability</h2><ul>')
    for source in snapshot['sources']:
        parts.append('<li>' + escape(source['id'] + ' / ' + source['provider'] + ': ' + source['availability'] + ' (' + source['reason'] + '), observed ' + source['observed_at']) + '</li>')
    parts.append('</ul><p>Availability is supplied by the exporter; it is not inferred from successful report generation. Stale sources are not fresh merely because the file was regenerated.</p></section>')
    parts.append('<section class="panel"><h2>Reported observations</h2><p>Showing up to ' + str(maximum) + ' of ' + str(len(snapshot['observations'])) + ' supplied observations, in exporter order. No cross-platform ranking is inferred.</p><label>Filter displayed rows<input id="search" type="search" autocomplete="off"></label><p id="visibleCount" role="status"></p><div class="scroll"><table><caption>Reported post and website measurements</caption><thead><tr>')
    headers = ['Platform / account', 'Format / topic', 'Publication state', 'Source', 'Views', 'Likes / replies / shares / saves', 'Interactions / views', 'Follows', 'Clicks', 'Enrollments / completions', 'Reported evidence']
    parts.extend('<th scope="col">' + escape(label) + '</th>' for label in headers)
    parts.append('</tr></thead><tbody>')
    for observation in snapshot['observations'][:maximum]:
        metrics = observation['metrics']
        source = sources[observation['source_id']]
        parts.append('<tr data-observation>')
        values = [observation['platform'] + ' / ' + observation['account_ref'], observation['format'] + ' / ' + observation['topic_ref'], observation['verification_state'], source['id'] + ' (' + source['availability'] + ')', metrics['views'], ' / '.join('Not reported' if metrics[key] is None else str(metrics[key]) for key in ['likes','replies','shares','saves']), interaction_ratio(metrics, source['availability']), metrics['follows'], metrics['link_clicks'], ' / '.join('Not reported' if metrics[key] is None else str(metrics[key]) for key in ['enrollments','completions']), '\n'.join(str(value) for value in [observation['permalink'],observation['verified_at'],observation['evidence_ref']] if value is not None) or 'Not supplied']
        parts.extend(cell(value) for value in values)
        parts.append('</tr>')
    parts.append('</tbody></table></div><p>Accepted/submitted is not verified-live. A reported verified-live state still needs genuine provider evidence. Views and conversion attribution differ by platform. The interaction ratio is a labelled calculation, not the platform-native engagement rate or proof of causal lift.</p></section>')
    parts.append('<section class="panel"><h2>Advisory review queue</h2>')
    if not snapshot['advisories']:
        parts.append('<p>No advisories supplied. No recommendations are invented.</p>')
    for advisory in snapshot['advisories']:
        parts.append('<article class="panel" data-advisory><h3>' + escape(advisory['id'] + ' / ' + advisory['action']) + '</h3><p>' + escape(advisory['reason']) + '</p><p>Observation references: ' + escape(', '.join(advisory['observation_ids'])) + '</p><p>Declared sample: ' + str(advisory['sample_size']) + '; configured minimum: ' + str(advisory['minimum_sample_size']) + '. Review required; sample declarations do not establish significance.</p><p>Advisory expiry: ' + escape(advisory['expires_at']) + '</p></article>')
    parts.append('</section><section class="panel"><h2>Metric definitions supplied by the exporter</h2><dl>')
    for key, value in snapshot['metric_definitions'].items():
        parts.append('<dt>' + escape(key) + '</dt><dd>' + escape(value) + '</dd>')
    parts.append('</dl></section><p>No actions were executed. Regenerate from a new validated export to refresh this report. Do not upload this data-filled file into the website repository.</p></main><script>' + SCRIPT + '</script></body></html>')
    return ''.join(parts)

def main():
    parser = argparse.ArgumentParser(description='Render a validated private steering snapshot to a local, read-only HTML dashboard.')
    parser.add_argument('snapshot', type=Path)
    parser.add_argument('--output', type=Path, default=Path.home()/'.local/share/209-steering/dashboard.html')
    parser.add_argument('--max-rows', type=int, default=500)
    args = parser.parse_args()
    source, output = args.snapshot.expanduser().resolve(), args.output.expanduser().resolve()
    if source.is_relative_to(REPOSITORY) or output.is_relative_to(REPOSITORY):
        raise SystemExit('Private snapshots and data-filled reports must be outside the website checkout.')
    if source == output or not 1 <= args.max_rows <= 1000:
        raise SystemExit('Choose a distinct output and 1–1000 displayed rows.')
    temporary = None
    try:
        if source.stat().st_size > 5000000:
            raise InvalidSnapshot('Snapshot exceeds 5 MB')
        snapshot = json.loads(source.read_text(encoding='utf-8'))
        schema = json.loads(Path(__file__).with_name('209-steering-snapshot.schema.json').read_text(encoding='utf-8'))
        now = dt.datetime.now(dt.timezone.utc)
        check(snapshot, schema, now=now)
        report = document(snapshot, now, args.max_rows)
        output.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=output.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(report)
        os.chmod(temporary, 0o600)
        os.replace(temporary, output)
        temporary = None
    except (OSError, ValueError, TypeError, KeyError):
        raise SystemExit('Report not generated. Check the local file, v1 contract, measurement window and expiry using the validator. No snapshot contents were logged; an older report, if present, was not refreshed.')
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    print(json.dumps({'report_written': True, 'operator_private': True, 'live_connected': False, 'actions_executed': False}))

if __name__ == '__main__':
    main()
