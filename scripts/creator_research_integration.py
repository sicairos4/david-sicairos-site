"""Callable research handoff and explicit CLI. No scheduling or dispatch.
Runtime and provider compatibility remain unverified.
"""
import argparse
import json
import os
from pathlib import Path
import tempfile

try:
    from .creator_research import query_perplexity_research
except ImportError:
    from creator_research import query_perplexity_research


def build_research_handoff(query, node, recency=None):
    if node not in ('personal', 'civic', 'wellness'):
        raise ValueError('node must be personal, civic, or wellness')
    research = query_perplexity_research(query, recency=recency)
    return {
        'schema_version': 1,
        'kind': 'creator_engine.research_handoff',
        'node': node,
        'status': 'needs_source_review',
        'research': research,
        'generation_constraints': {
            'preserve_source_attribution': True,
            'do_not_invent_metrics': True,
            'distinguish_facts_from_inference': True,
            'private_planner_content_allowed': False,
        },
        'publication_approved': False,
        'dispatch_approved': False,
    }


def write_handoff(handoff, destination):
    target = Path(destination).expanduser()
    if not target.parent.is_dir():
        raise ValueError('Output parent directory must already exist')
    encoded = json.dumps(handoff, ensure_ascii=False, indent=2) + '\n'
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode='w', encoding='utf-8', dir=target.parent,
            prefix='.creator-research-', delete=False,
        ) as stream:
            temporary = Path(stream.name)
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, target)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return target


def main():
    parser = argparse.ArgumentParser(description='Create a source-preserving research handoff; never publish or email.')
    parser.add_argument('--query', required=True)
    parser.add_argument('--node', required=True, choices=['personal', 'civic', 'wellness'])
    parser.add_argument('--recency', choices=['hour', 'day', 'week', 'month', 'year'])
    parser.add_argument('--output', required=True, help='New JSON file; existing files are never overwritten')
    args = parser.parse_args()
    target = Path(args.output).expanduser()
    if target.exists() or target.is_symlink() or not target.parent.is_dir():
        parser.error('Output must be a new file inside an existing directory')
    try:
        handoff = build_research_handoff(args.query, args.node, args.recency)
        write_handoff(handoff, target)
    except (ValueError, RuntimeError, OSError) as exc:
        parser.exit(1, 'Research integration failed (' + type(exc).__name__ + '); no dispatch performed.\n')


if __name__ == '__main__':
    main()
