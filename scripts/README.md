# Script directory guide

Run existing commands from the repository root unless their operating guide says otherwise. This directory includes provider calls, private-data tools, imports, exporters, source generators, and checks. A filename is not authorization to execute it.

## Creator Engine

- `creator_engine.py`: runner implementation. Use the preserved root entry point `python creator_engine_bus.py ...`.
- `creator_research.py` and `creator_research_integration.py`: research and source-preserving handoff.
- `creator_generation.py`: explicitly requested provider generation.
- `creator_muse_handoff.py`: review payload construction, not publication.
- `creator_run_state.py`: opt-in local checkpoints.

The root compatibility module resolves imports to `scripts.creator_engine`, avoiding two independent implementations. Source fingerprints include both the root entry point and implementation. See `../docs/creator-engine-operation.md`; old checkpoints may not match the reorganized source.

## Public site data

- `collect-social-showcase.py`: public Bluesky and YouTube source collection.
- `add-linkedin-showcase.py`: idempotent merge of selected LinkedIn previews; not automatic account discovery.
- `export-social-feed.py`: configured public feed export.
- `import-beehiiv.py` and `import_public_files.py`: content imports.

These paths remain unchanged because existing workflow and operational references use them. Read the corresponding script and guide before executing it; credentials, remote requests, and output writes differ by tool.

## Archive and private-data operations

The `prepare_*`, `search_private_archive.py`, `sync_public_files_drive.py`, `split_bundles.py`, `validate_bundle_manifest.py`, and `archive_import_template.psql` files remain in their established locations. Review their individual input/output boundaries. Do not commit private inputs, generated private records, or credentials to public site data.

## Workstation and development helpers

`apply-209-brand.py`, the workstation configuration/implementation/finish helpers, Codespace setup scripts, and priority-bundle scripts retain their existing paths. They can modify source or invoke other operations; this guide does not execute them.

## Checks

Existing `audit-*` and `test-*` scripts remain here for compatibility. The separate `../tests/` directory also contains checks. No audit, test, provider call, or deployment is executed by this organizational change. A later relocation of checks must update every caller rather than copying files and leaving two active versions.

## Organization rules

Keep shared Creator Engine implementation here rather than adding business logic to root launchers. Document new operational tools and their side effects. Do not merge `worker/` with `workers/`, relocate public pages, or move workflow-referenced scripts based only on similar names. Map consumers first, then move and update references as one scoped change.
