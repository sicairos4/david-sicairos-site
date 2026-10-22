"""Creator Engine research, optional generation, and Muse payload runner.
Explicit invocation calls configured providers and writes one local JSON bundle.
No database insertion, email, scheduling, or publication. Execution remains deferred.
"""
import argparse
from pathlib import Path

from scripts.creator_research_integration import build_research_handoff, write_handoff
from scripts.creator_muse_handoff import build_muse_queue_payload
from scripts.creator_generation import PLATFORMS, generation_config, generate_draft


def run_creator_engine(query, node, title, destination, recency=None, generated_draft=None, generate=False, platforms=()):
    target = Path(destination).expanduser()
    if target.exists() or target.is_symlink():
        raise ValueError('Output already exists; choose a new file')
    if not target.parent.is_dir():
        raise ValueError('Output parent directory must already exist')
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
    if generate:
        generation_config()
    handoff = build_research_handoff(query, node, recency=recency)
    generation = generate_draft(handoff, platforms=platforms) if generate else None
    draft = generation['text'] if generation else generated_draft
    queue_payload = build_muse_queue_payload(handoff, title, generated_draft=draft)
    bundle = {
        'schema_version': 1,
        'kind': 'creator_engine.run_bundle',
        'status': 'prepared_for_review',
        'research_handoff': handoff,
        'muse_queue': {'table': 'muse_record_queue', 'payload': queue_payload, 'inserted': False},
        'generation': {
            'performed': generation is not None,
            'external_draft_supplied': generated_draft is not None,
            'result': generation,
        },
        'delivery': {'attempted': False, 'receipt': None},
        'publication_approved': False,
        'dispatch_approved': False,
    }
    write_handoff(bundle, target)
    return bundle


def main():
    parser = argparse.ArgumentParser(description='Research -> optional Gemini drafts -> Muse review payload -> local JSON. No dispatch.')
    parser.add_argument('--query', required=True)
    parser.add_argument('--node', required=True, choices=['personal', 'civic', 'wellness'])
    parser.add_argument('--title', required=True)
    parser.add_argument('--recency', choices=['hour', 'day', 'week', 'month', 'year'])
    drafts = parser.add_mutually_exclusive_group()
    drafts.add_argument('--draft-file', help='Optional existing UTF-8 draft')
    drafts.add_argument('--generate', action='store_true', help='Explicitly call Gemini; requires GEMINI_API_KEY and GEMINI_MODEL')
    parser.add_argument('--platform', action='append', choices=PLATFORMS, default=[], help='Repeat for requested variants; requires --generate')
    parser.add_argument('--output', required=True, help='New JSON file inside an existing directory')
    args = parser.parse_args()
    try:
        draft = Path(args.draft_file).expanduser().read_text(encoding='utf-8') if args.draft_file else None
        run_creator_engine(
            query=args.query, node=args.node, title=args.title, destination=args.output,
            recency=args.recency, generated_draft=draft, generate=args.generate,
            platforms=tuple(dict.fromkeys(args.platform)),
        )
    except (ValueError, RuntimeError, OSError, UnicodeError) as exc:
        parser.exit(1, 'Creator Engine failed (' + type(exc).__name__ + '); no dispatch performed.\n')


if __name__ == '__main__':
    main()
