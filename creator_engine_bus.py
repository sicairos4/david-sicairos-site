"""Research, optional generation, local checkpoints, and Muse payload runner.
No database insertion, email, schedule, or publication. Execution remains deferred.
"""
import argparse
from contextlib import nullcontext
import hashlib
import os
from pathlib import Path

from scripts.creator_research_integration import build_research_handoff, write_handoff
from scripts.creator_muse_handoff import build_muse_queue_payload
from scripts.creator_generation import PLATFORMS, generation_config, generate_draft
from scripts.creator_run_state import RunState


def run_creator_engine(query, node, title, destination, recency=None, generated_draft=None, generate=False, platforms=(), state_dir=None, run_key=None):
    target = Path(destination).expanduser()
    if target.exists() or target.is_symlink():
        raise ValueError('Output already exists; choose a new file')
    if not target.parent.is_dir():
        raise ValueError('Output parent directory must already exist')
    if not isinstance(query, str) or not query.strip():
        raise ValueError('Research query is required')
    if node not in ('personal', 'civic', 'wellness'):
        raise ValueError('Unknown content node')
    if not isinstance(title, str) or not title.strip():
        raise ValueError('A review title is required')
    if generated_draft is not None and not isinstance(generated_draft, str):
        raise ValueError('Draft must be text or None')
    if generate and generated_draft is not None:
        raise ValueError('Choose generation or an existing draft, not both')
    if platforms and not generate:
        raise ValueError('Platform variants require explicit generation')
    if any(platform not in PLATFORMS for platform in platforms):
        raise ValueError('Unsupported platform')
    if bool(state_dir) != bool(run_key):
        raise ValueError('State directory and nonempty run key must be supplied together')
    if generate:
        generation_config()
    identity = {
        'run_key': run_key, 'query': query, 'node': node, 'title': title,
        'recency': recency, 'generate': generate, 'platforms': list(platforms),
        'model': os.environ.get('GEMINI_MODEL', '') if generate else None,
        'draft_sha256': hashlib.sha256(generated_draft.encode('utf-8')).hexdigest() if generated_draft is not None else None,
    }
    if state_dir:
        root = Path(__file__).resolve().parent
        paths = ['creator_engine_bus.py', 'scripts/creator_research.py', 'scripts/creator_research_integration.py',
                 'scripts/creator_generation.py', 'scripts/creator_muse_handoff.py',
                 'scripts/creator_run_state.py', 'prompts/creator-engine-draft-contract.txt']
        identity['source_fingerprints'] = {path: hashlib.sha256((root / path).read_bytes()).hexdigest() for path in paths}
    context = RunState(state_dir, identity) if state_dir else nullcontext(None)
    with context as state:
        research_call = lambda: build_research_handoff(query, node, recency=recency)
        handoff = state.stage('research', research_call) if state else research_call()
        generation = None
        if generate:
            generation_call = lambda: generate_draft(handoff, platforms=platforms)
            generation = state.stage('generation', generation_call) if state else generation_call()
        if state:
            state.check_pause()
        draft = generation['text'] if generation else generated_draft
        queue_payload = build_muse_queue_payload(handoff, title, generated_draft=draft)
        bundle = {
            'schema_version': 1, 'kind': 'creator_engine.run_bundle', 'status': 'prepared_for_review',
            'run_id': state.run_id if state else None,
            'research_handoff': handoff,
            'muse_queue': {'table': 'muse_record_queue', 'payload': queue_payload, 'inserted': False},
            'generation': {
                'performed': generation is not None,
                'external_draft_supplied': generated_draft is not None, 'result': generation,
                'performed_describes': 'bundle contents, including reused checkpoints; not necessarily this invocation',
            },
            'delivery': {'attempted': False, 'receipt': None},
            'publication_approved': False, 'dispatch_approved': False,
        }
        write_handoff(bundle, target)
        return bundle


def main():
    parser = argparse.ArgumentParser(description='Research -> optional drafts -> Muse payload -> local JSON. No dispatch.')
    parser.add_argument('--query', required=True)
    parser.add_argument('--node', required=True, choices=['personal', 'civic', 'wellness'])
    parser.add_argument('--title', required=True)
    parser.add_argument('--recency', choices=['hour', 'day', 'week', 'month', 'year'])
    drafts = parser.add_mutually_exclusive_group()
    drafts.add_argument('--draft-file', help='Optional existing UTF-8 draft')
    drafts.add_argument('--generate', action='store_true', help='Call Gemini; requires GEMINI_API_KEY and GEMINI_MODEL')
    parser.add_argument('--platform', action='append', choices=PLATFORMS, default=[])
    parser.add_argument('--state-dir', help='Existing trusted private directory for opt-in checkpoints')
    parser.add_argument('--run-key', help='Owner-selected freshness key; required with --state-dir')
    parser.add_argument('--output', required=True, help='New JSON file inside an existing directory')
    args = parser.parse_args()
    try:
        draft = Path(args.draft_file).expanduser().read_text(encoding='utf-8') if args.draft_file else None
        run_creator_engine(
            query=args.query, node=args.node, title=args.title, destination=args.output,
            recency=args.recency, generated_draft=draft, generate=args.generate,
            platforms=tuple(dict.fromkeys(args.platform)), state_dir=args.state_dir, run_key=args.run_key,
        )
    except (ValueError, RuntimeError, OSError, UnicodeError, KeyError, TypeError) as exc:
        parser.exit(1, 'Creator Engine failed (' + type(exc).__name__ + '); no dispatch performed.\n')


if __name__ == '__main__':
    main()
