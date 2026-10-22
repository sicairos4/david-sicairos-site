# Creator Engine source handoff

## Implemented source

- `scripts/creator_research.py`: owner-supplied Sonar request shape, bounded retry handling, response metadata preservation.
- `scripts/creator_research_integration.py`: research handoff and new-file JSON writer.
- `scripts/creator_muse_handoff.py`: payload builder for existing `muse_record_queue`; does not insert records.
- `creator_engine_bus.py`: connects research, handoff, queue payload, and local bundle output.
- `.github/workflows/creator_engine_cron.yml`: manual invocation only despite legacy target filename; no cron schedule.
- `prompts/creator-engine-draft-contract.txt`: proposed prompt, not connected to a model.

## Explicit execution effects

Invoking the runner or dispatching the workflow makes a paid-provider research request when credentials permit. It writes a JSON bundle; workflow execution also uploads that bundle as a GitHub Actions artifact retained for seven days. Do not include secrets, private planner writing, or private archive contents in workflow inputs. Repository and artifact access must be considered before dispatch.

The workflow references `PERPLEXITY_API_KEY` without creating or changing the secret. It contains no tests, publication step, database write, Gemini call, email, or schedule. Existing repository workflows are not disabled or changed.

## Local invocation (not executed)

From the repository root, with an existing output directory and the API key supplied through the environment:

```sh
python creator_engine_bus.py --query 'City of Atwater official public meeting information' --node civic --title 'Atwater research draft' --output output/review-bundle.json
```

The output path must not already exist. `--recency` is optional. `--draft-file` accepts existing UTF-8 text; it does not generate text. Source metadata is retained, not fact-checked. A URL's presence does not establish that it supports a claim.

## Outstanding implementation and owner gates

Gemini generation, authorized analytics ingestion, steering-vector application, durable Muse intake, provider delivery receipts, deduplication across runs, approved posting, and scheduling remain open. Review existing publisher interfaces before adding these integrations. No replacement course assets, prices, credentials, release destinations, or signing identity are selected here.

## Status

All execution, tests, API compatibility checks, deployment checks, and live acceptance are deferred at the owner's request. Source commits do not establish operational success. This batch does not complete the broader workstation, learning, public-records, website, or Android checklists.
