# MCP dependency integration

This source connects get_system_status to the existing restricted public.v_triad_live_health view. The returned field allowlist excludes unexpected future columns. Coverage is publishing_209 only and does not certify platform availability or publication.

ask_gemini now requires existing task_id, content_id and verified_evidence objects with url, claim and source_type primary. Only editorial_review is accepted. Refresh tool discovery and migrate question only callers. URL and packet validation do not establish independent source verification. The deployed advisor version 5 accepts this packet and the existing Muse bridge forwards it.

Preserve verify_jwt false for MCP because its body performs bearer authorization. Preserve advisor JWT verification true. Preserve bridge credentials, task authorization, existing queues, cadence and platform state. No worker registration, arbitrary task claim, completion, webhook retry or publishing tool is added.

Dependencies still requiring verification: MCP_ACCESS_TOKEN present and at least 32 characters, secure Supabase runtime environment, MUSE_BRIDGE_TOKEN for advice, advisor provider configuration, PostgREST visibility and service role access to the health view, authenticated transport initialization, tools/list, tool calls and SDK session behavior. This source does not promise a session header or install a persistent worker.

No secret values are included. Current n8n health reported its runtime configuration missing. Do not paste keys into Git or chat. Establish that instance through its secure configuration before binding the MCP credential.

This commit is source control, not a deployment or runtime success receipt. Type checking and authenticated integration verification remain required. Deployment must use the exact source, entrypoint_path index.ts, import_map_path deno.json and verify_jwt false, with separate exact action approval. No broad test suite is authorized by this document.
