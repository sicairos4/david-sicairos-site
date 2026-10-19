import argparse
import datetime as dt
import json
from pathlib import Path
import re
from urllib.parse import urlsplit, parse_qs
from zoneinfo import ZoneInfo

class InvalidSnapshot(ValueError):
    pass

def fail(path, reason):
    raise InvalidSnapshot(path + ': ' + reason)

def timestamp(value):
    parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('Timezone required')
    return parsed.astimezone(dt.timezone.utc)

def validate(value, schema, path='$'):
    if 'const' in schema and (type(value) is not type(schema['const']) or value != schema['const']):
        fail(path, 'unexpected constant')
    if 'enum' in schema and value not in schema['enum']:
        fail(path, 'unsupported value')
    types = schema.get('type', [])
    types = [types] if isinstance(types, str) else types
    matches = {'object': isinstance(value, dict), 'array': isinstance(value, list), 'string': isinstance(value, str), 'integer': type(value) is int, 'null': value is None}
    if types and not any(matches.get(t, False) for t in types):
        fail(path, 'wrong type')
    if isinstance(value, dict):
        properties = schema.get('properties', {})
        if schema.get('additionalProperties') is False and set(value) - set(properties):
            fail(path, 'unknown fields are not permitted')
        if set(schema.get('required', [])) - set(value):
            fail(path, 'required fields missing')
        for key, item in value.items():
            if key in properties:
                validate(item, properties[key], path + '.' + key)
    elif isinstance(value, list):
        if len(value) < schema.get('minItems', 0) or len(value) > schema.get('maxItems', 10000):
            fail(path, 'unsupported list size')
        if schema.get('uniqueItems') and len({json.dumps(v, sort_keys=True) for v in value}) != len(value):
            fail(path, 'duplicate items')
        for index, item in enumerate(value):
            validate(item, schema.get('items', {}), path + '[' + str(index) + ']')
    elif isinstance(value, str):
        if len(value) < schema.get('minLength', 0) or len(value) > schema.get('maxLength', 100000):
            fail(path, 'unsupported text length')
        if schema.get('pattern') and re.search(schema['pattern'], value) is None:
            fail(path, 'unsupported text format')
        if schema.get('format') == 'date-time':
            try:
                timestamp(value)
            except (ValueError, TypeError, OverflowError):
                fail(path, 'invalid timestamp or missing timezone')
        if schema.get('format') == 'https-url':
            parsed = urlsplit(value)
            if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
                fail(path, 'HTTPS permalink required without credentials or fragments')
            if set(parse_qs(parsed.query)) - {'v', 'id', 'story_fbid'}:
                fail(path, 'unexpected query parameters')
    elif type(value) is int:
        if value < schema.get('minimum', value) or value > schema.get('maximum', value):
            fail(path, 'number out of range')

def check(snapshot, schema, now=None):
    validate(snapshot, schema)
    now = now or dt.datetime.now(dt.timezone.utc)
    generated = timestamp(snapshot['generated_at'])
    if generated > now + dt.timedelta(seconds=300):
        fail('$.generated_at', 'snapshot is in the future')
    if (now - generated).total_seconds() > snapshot['max_age_seconds']:
        fail('$.generated_at', 'snapshot expired; do not apply advisories')
    window = snapshot['window']
    if timestamp(window['start']) >= timestamp(window['end']) or timestamp(window['end']) > generated:
        fail('$.window', 'invalid measurement window')
    try:
        ZoneInfo(window['timezone'])
    except (KeyError, ValueError):
        fail('$.window.timezone', 'unknown IANA timezone')
    source_ids = [s['id'] for s in snapshot['sources']]
    observation_ids = [o['id'] for o in snapshot['observations']]
    advisory_ids = [a['id'] for a in snapshot['advisories']]
    for name, ids in [('sources', source_ids), ('observations', observation_ids), ('advisories', advisory_ids)]:
        if len(set(ids)) != len(ids):
            fail('$.' + name, 'IDs must be unique')
    sources = {s['id']: s for s in snapshot['sources']}
    observations = {o['id']: o for o in snapshot['observations']}
    for source in sources.values():
        if timestamp(source['observed_at']) > generated:
            fail('$.sources', 'observation time exceeds generation time')
    for observation in observations.values():
        if observation['source_id'] not in sources:
            fail('$.observations', 'unknown source reference')
        if timestamp(observation['observed_at']) > generated:
            fail('$.observations', 'future observation')
        if sources[observation['source_id']]['availability'] == 'unavailable' and any(v is not None for v in observation['metrics'].values()):
            fail('$.observations.metrics', 'unavailable metrics must be null, not invented zeros')
        if observation['verification_state'] == 'verified_live':
            if not observation['permalink'] or not observation['verified_at'] or not observation['evidence_ref']:
                fail('$.observations', 'verified-live needs permalink, timestamp and evidence reference')
            if timestamp(observation['verified_at']) > generated:
                fail('$.observations', 'future verification')
    for advisory in snapshot['advisories']:
        if any(ref not in observations for ref in advisory['observation_ids']):
            fail('$.advisories', 'unknown observation reference')
        if advisory['sample_size'] < advisory['minimum_sample_size']:
            fail('$.advisories', 'insufficient declared sample; no promotion or actuation')
        if timestamp(advisory['expires_at']) <= now:
            fail('$.advisories', 'advisory expired')
    return {'valid_structure': True, 'mode': 'advisory', 'publication_authorized': False, 'evidence_independently_verified': False, 'observations': len(observations), 'advisories': len(advisory_ids)}

def main():
    parser = argparse.ArgumentParser(description='Validate an operator-private advisory snapshot without network or execution.')
    parser.add_argument('snapshot', type=Path)
    parser.add_argument('--schema', type=Path, default=Path(__file__).with_name('209-steering-snapshot.schema.json'))
    args = parser.parse_args()
    if args.snapshot.stat().st_size > 5000000:
        raise SystemExit('Snapshot exceeds 5 MB')
    try:
        snapshot = json.loads(args.snapshot.read_text(encoding='utf-8'))
        schema = json.loads(args.schema.read_text(encoding='utf-8'))
        result = check(snapshot, schema)
    except (InvalidSnapshot, ValueError, OSError) as error:
        print(json.dumps({'valid_structure': False, 'reason': str(error)}))
        raise SystemExit(1)
    print(json.dumps(result))

if __name__ == '__main__':
    main()
