"""Build payloads for existing muse_record_queue. No database or network writes.
Source-only implementation; not tested or live-verified.
"""
import json
from urllib.parse import urlsplit


def _source_urls(research):
    urls = []
    candidates = []
    citations = research.get('citations', [])
    results = research.get('search_results', [])
    if isinstance(citations, list):
        candidates.extend(citations)
    if isinstance(results, list):
        candidates.extend(item.get('url') for item in results if isinstance(item, dict))
    for candidate in candidates:
        if not isinstance(candidate, str):
            continue
        try:
            parsed = urlsplit(candidate)
            allowed = parsed.scheme in ('https', 'http') and bool(parsed.hostname)
        except ValueError:
            allowed = False
        if allowed and candidate not in urls:
            urls.append(candidate)
    return urls


def build_muse_queue_payload(handoff, title, generated_draft=None):
    if not isinstance(handoff, dict) or handoff.get('kind') != 'creator_engine.research_handoff':
        raise ValueError('Expected a Creator Engine research handoff')
    if not isinstance(title, str) or not title.strip():
        raise ValueError('A review title is required')
    node = handoff.get('node')
    if node not in ('personal', 'civic', 'wellness'):
        raise ValueError('Unknown content node')
    research = handoff.get('research')
    if not isinstance(research, dict) or not isinstance(research.get('content'), str) or not research['content'].strip():
        raise ValueError('Research content is required')
    if generated_draft is not None and not isinstance(generated_draft, str):
        raise ValueError('Draft must be text or None')
    urls = _source_urls(research)
    envelope = {
        'schema_version': 1,
        'kind': 'creator_engine.muse_review',
        'handoff': handoff,
        'generated_draft': generated_draft,
        'source_urls': urls,
        'review_warnings': [] if urls else ['No usable source URLs; source review required'],
        'publication_approved': False,
        'dispatch_approved': False,
    }
    return {
        'title': title.strip(),
        'source_url': urls[0] if urls else None,
        'category': 'creator_engine:' + node,
        'status': 'needs_review',
        'signal_draft': json.dumps(envelope, ensure_ascii=False),
    }
