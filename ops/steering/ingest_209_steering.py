import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

from validate_209_steering import check, timestamp, InvalidSnapshot

REPOSITORY = Path(__file__).resolve().parents[2]

def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InvalidSnapshot('Duplicate JSON keys are not permitted.')
        result[key] = value
    return result

def reject_constant(value):
    raise InvalidSnapshot('Non-finite JSON numbers are not permitted.')

def decode(text):
    return json.loads(text, object_pairs_hook=unique_object, parse_constant=reject_constant)

def intake_policy(snapshot):
    generated = timestamp(snapshot['generated_at'])
    age = dt.timedelta(seconds=snapshot['max_age_seconds'])
    sources = {source['id']: source for source in snapshot['sources']}
    observations = {item['id']: item for item in snapshot['observations']}
    for advisory in snapshot['advisories']:
        expires = timestamp(advisory['expires_at'])
        if not generated < expires <= generated + age:
            raise InvalidSnapshot('Advisories must expire within the snapshot lifetime.')
        for reference in advisory['observation_ids']:
            observation = observations[reference]
            source = sources[observation['source_id']]
            if source['availability'] != 'available' or source['reason'] != 'ok':
                raise InvalidSnapshot('An advisory references an unavailable or stale source.')
            if generated - timestamp(source['observed_at']) > age or generated - timestamp(observation['observed_at']) > age:
                raise InvalidSnapshot('An advisory references an old collection timestamp.')
            if all(value is None for value in observation['metrics'].values()):
                raise InvalidSnapshot('An advisory has no reported metrics to review.')

def write_private(path, data):
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'wb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())

def existing_bundle(destination, payload, digest, needs_report):
    snapshot = destination / 'snapshot.json'
    receipt = destination / 'receipt.json'
    if destination.is_symlink() or snapshot.is_symlink() or receipt.is_symlink():
        raise InvalidSnapshot('Refusing symbolic links in an existing bundle.')
    if snapshot.read_bytes() != payload:
        raise InvalidSnapshot('An existing bundle does not match this payload.')
    recorded = decode(receipt.read_text(encoding='utf-8'))
    if recorded.get('snapshot_sha256') != digest or recorded.get('publication_authorized') is not False:
        raise InvalidSnapshot('An existing receipt does not match the review-only bundle.')
    if needs_report and not (destination / 'dashboard.html').is_file():
        raise InvalidSnapshot('Existing bundle has no dashboard. Use the standalone renderer outside the checkout.')

def main():
    parser = argparse.ArgumentParser(description='Accept a v1 advisory snapshot into a private local review bundle. No network or publishing.')
    parser.add_argument('snapshot', type=Path)
    parser.add_argument('--directory', type=Path, default=Path.home()/'.local/share/209-steering/inbox')
    parser.add_argument('--render', action='store_true', help='Also create the local read-only dashboard.')
    parser.add_argument('--max-rows', type=int, default=500)
    args = parser.parse_args()
    source, directory = args.snapshot.expanduser().resolve(), args.directory.expanduser().resolve()
    if source.is_relative_to(REPOSITORY) or directory.is_relative_to(REPOSITORY):
        raise SystemExit('Private input and review bundles must be outside the website checkout.')
    if not 1 <= args.max_rows <= 1000:
        raise SystemExit('Display limit must be from 1 to 1000 rows.')
    staging = None
    try:
        if source.stat().st_size > 5000000:
            raise InvalidSnapshot('Snapshot exceeds 5 MB.')
        snapshot = decode(source.read_text(encoding='utf-8'))
        schema = decode(Path(__file__).with_name('209-steering-snapshot.schema.json').read_text(encoding='utf-8'))
        now = dt.datetime.now(dt.timezone.utc)
        check(snapshot, schema, now=now)
        intake_policy(snapshot)
        payload = (json.dumps(snapshot, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode('utf-8')
        digest = hashlib.sha256(payload).hexdigest()
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        if os.name == 'posix':
            info = directory.stat()
            if info.st_uid != os.getuid() or info.st_mode & 0o077:
                raise InvalidSnapshot('Choose an operator-owned intake directory with owner-only permissions.')
        destination = directory / digest
        if destination.exists():
            existing_bundle(destination, payload, digest, args.render)
            print(json.dumps({'status':'already_present','bundle_id':digest,'live_connected':False,'publication_authorized':False}))
            return
        staging = Path(tempfile.mkdtemp(prefix='.incoming-', dir=directory))
        write_private(staging/'snapshot.json', payload)
        receipt = {'schema_version':1,'status':'accepted_for_local_review','accepted_at_utc':now.isoformat(),'snapshot_id':snapshot['snapshot_id'],'snapshot_sha256':digest,'mode':'advisory','visibility':'operator_private','observation_count':len(snapshot['observations']),'advisory_count':len(snapshot['advisories']),'structure_and_intake_policy_passed':True,'provider_evidence_independently_verified':False,'live_connected':False,'publication_authorized':False}
        if args.render:
            from render_209_steering import document
            report = document(snapshot, now, args.max_rows).encode('utf-8')
            write_private(staging/'dashboard.html', report)
            receipt['dashboard_sha256'] = hashlib.sha256(report).hexdigest()
        write_private(staging/'receipt.json', (json.dumps(receipt, indent=2)+'\n').encode('utf-8'))
        try:
            os.rename(staging, destination)
            staging = None
            status = 'accepted_for_local_review'
        except OSError:
            if not destination.exists():
                raise
            existing_bundle(destination, payload, digest, args.render)
            status = 'already_present'
        print(json.dumps({'status':status,'bundle_id':digest,'live_connected':False,'publication_authorized':False}))
    except InvalidSnapshot as error:
        print(json.dumps({'status':'rejected','reason':str(error),'publication_authorized':False}))
        raise SystemExit(1)
    except (OSError, ValueError, TypeError, KeyError, OverflowError, RecursionError):
        print(json.dumps({'status':'rejected','reason':'Local read, validation or bundle write failed. No snapshot contents or credentials are logged.','publication_authorized':False}))
        raise SystemExit(1)
    finally:
        if staging is not None:
            shutil.rmtree(staging, ignore_errors=True)

if __name__ == '__main__':
    main()
