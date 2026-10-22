# Creator Engine operating guide

## Source pipeline

`creator_engine_bus.py` connects Perplexity research, the source-preserving handoff, optional Gemini generation, the existing Muse queue payload shape, and a single local JSON bundle.

Modules:
- `scripts/creator_research.py`: research request and provider metadata.
- `scripts/creator_research_integration.py`: research envelope and non-overwriting JSON writer.
- `scripts/creator_generation.py`: explicit Gemini generation using the committed prompt.
- `scripts/creator_muse_handoff.py`: payload builder for `muse_record_queue`; no insertion.
- `prompts/creator-engine-draft-contract.txt`: generation instructions loaded when generation is requested. Its earlier proposed-status wording describes its origin, not an approval to publish.

## Configuration

Supply `PERPLEXITY_API_KEY` through the environment for local research or the identically named repository secret for the workflow. Generation additionally requires `GEMINI_API_KEY` and a bare model identifier in `GEMINI_MODEL`. The workflow reads that identifier from the repository variable `GEMINI_MODEL`. No model is selected by the code. This commit does not set any secret or variable. Never commit actual credentials.

## Local commands (not executed)

Run from the repository root after creating the output directory. Choose a new output path each time. These commands contact providers and can incur charges.

Research only:

```sh
python creator_engine_bus.py --query 'City of Atwater official public meeting information' --node civic --title 'Atwater research draft' --output output/review-bundle.json
```

Research plus draft generation:

```sh
python creator_engine_bus.py --query 'City of Atwater official public meeting information' --node civic --title 'Atwater draft variants' --generate --platform facebook --platform newsletter --output output/generated-review-bundle.json
```

Alternatively, supply an existing UTF-8 draft with `--draft-file`. It cannot be combined with `--generate`. `--recency` is optional. Generation requires source metadata, but source metadata does not prove factual accuracy or claim support.

## Manual workflow

`.github/workflows/creator_engine_cron.yml` has only `workflow_dispatch`, despite its filename. It has no cron, push, or pull-request trigger. No workflow is dispatched by these source changes. Availability in GitHub Actions remains unestablished until the workflow is in the appropriate repository configuration; no default-branch merge is performed here.

Inputs are query, title, node, recency, generation switch, and optional comma-separated platform names. Generation defaults off. Supported variants are facebook, instagram, threads, linkedin, bluesky, newsletter, and youtube. The workflow passes inputs through environment variables and quoted command arguments. It contains no tests.

Explicit dispatch calls Perplexity and, if requested, Gemini. On success it uploads the review bundle as an Actions artifact with seven-day retention. Treat workflow inputs, logs, and artifacts according to repository visibility and access. Do not supply private planner writing, secrets, or private archive material. Artifact creation is not a Muse delivery receipt or publication receipt.

## Output and failure boundary

The bundle retains research, generation output and metadata when requested, and the Muse queue payload. Its queue status is `needs_review`. Insertion and delivery are recorded as not performed; dispatch and publication approval remain false. These fields describe this run, not any later external activity.

The output writer refuses existing destination files. Provider failure stops the run; if generation fails after research, the current runner does not persist a research-only checkpoint. Provider charges can occur before a later stage fails. Gemini requests have no automatic retry. Perplexity retries are bounded. There is no persistent cross-run deduplication or delivery retry queue.

## Still outside this implementation

Authorized analytics ingestion and steering-vector application, durable Muse intake, email delivery, delivery receipts, cross-run duplicate prevention, pause/retry operations, scheduling, human approval interfaces, and public posting remain open. Integrate with the existing publisher rather than creating a parallel one. No database, credentials, posting destinations, prices, course assets, public records, or signing identities are changed here.

## Verification status

Tests, execution, API compatibility checks, builds, deployment, and browser/device acceptance remain deferred at the owner's request. Committed source is not evidence of operational success. Existing repository workflows are not disabled. The broader workstation, learning, public-records, website, and Android checklists remain separate.
