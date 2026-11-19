/**
 * Cloudflare Worker Route: Meta Threads Graph API Relay, Auto Token Rotation & Repair Surgeon Retry
 * Repo: sicairos4/david-sicairos-site
 * Schema: publishing_209 (ai_tasks, diagnostic_traces, repair_logs)
 */

export interface Env {
  THREADS_USER_ID: string;           // Numeric Threads User ID for 209media.connect
  THREADS_ACCESS_TOKEN: string;      // Initial long-lived token (60-day rolling refresh)
  THREADS_KV?: KVNamespace;          // Optional KV binding for rolling token persistence
  ZAPIER_WEBHOOK_SECRET: string;     // Bearer token shared with Zapier & internal workers
  SUPABASE_URL: string;              // https://uwidjnnhdgtrpsymuhwp.supabase.co
  SUPABASE_SERVICE_ROLE_KEY: string; // Service role key for publishing_209 writes
}

interface ZapierThreadsPayload {
  task_id?: string;
  content_id?: string;
  vertical?: "personal_apex" | "civic_oversight" | "bio_performance";
  text: string;
  media_type?: "TEXT" | "IMAGE" | "VIDEO";
  image_url?: string;
  video_url?: string;
  link_attachment?: string;
  topic_tag?: string;
  reply_to_id?: string;
  is_made_with_ai?: boolean;
}

interface RepairRetryPayload {
  task_id?: string;
  limit?: number;
}

interface AiTaskRow {
  task_id: string;
  content_id: string;
  vertical?: string;
  status: string;
  hop_count?: number;
  max_hops?: number;
  output_payload?: {
    surface?: string;
    creation_id?: string | null;
    threads_post_id?: string | null;
    sanitized_text?: string | null;
    media_type?: "TEXT" | "IMAGE" | "VIDEO";
    image_url?: string | null;
    video_url?: string | null;
    link_attachment?: string | null;
    error?: string | null;
  };
}

const THREADS_GRAPH_BASE = "https://graph.threads.net/v1.0";
const KV_TOKEN_KEY = "threads:209media:access_token";
const KV_TOKEN_META_KEY = "threads:209media:token_meta";

/**
 * Enforces zero hyphens or dashes per Creator Engine stylometric rules
 * while preserving URLs inside the payload.
 */
export function sanitizeCopy(raw: string): string {
  return raw
    .split(/(\s+)/)
    .map((token) => {
      if (/^https?:\/\//i.test(token)) return token;
      return token
        .replace(/[\u2012\u2013\u2014\u2015\u2212-]/g, " ")
        .replace(/\s{2,}/g, " ");
    })
    .join("")
    .trim();
}

function assertThreadsByteLimit(text: string, maxBytes = 500): void {
  const byteLength = new TextEncoder().encode(text).length;
  if (byteLength > maxBytes) {
    throw new Error(`Threads text exceeds ${maxBytes} UTF8 bytes (${byteLength} bytes).`);
  }
}

function supabaseHeaders(env: Env, prefer?: string): Record<string, string> {
  const headers: Record<string, string> = {
    apikey: env.SUPABASE_SERVICE_ROLE_KEY,
    Authorization: `Bearer ${env.SUPABASE_SERVICE_ROLE_KEY}`,
    "Content-Type": "application/json",
    "Accept-Profile": "publishing_209",
    "Content-Profile": "publishing_209",
  };
  if (prefer) headers["Prefer"] = prefer;
  return headers;
}

/**
 * Retrieves the active rolling Threads token from Workers KV first,
 * falling back to the THREADS_ACCESS_TOKEN secret.
 */
export async function getActiveThreadsToken(env: Env): Promise<string> {
  if (env.THREADS_KV) {
    const kvToken = await env.THREADS_KV.get(KV_TOKEN_KEY);
    if (kvToken && kvToken.trim().length > 0) {
      return kvToken.trim();
    }
  }
  return env.THREADS_ACCESS_TOKEN;
}

/**
 * Exchanges a valid long-lived Threads token for a fresh 60-day token
 * via GET https://graph.threads.net/refresh_access_token and stores it in KV.
 * Run on a Cron trigger (e.g. every 15 days) for uninterrupted rolling validity.
 */
export async function refreshThreadsAccessToken(env: Env): Promise<{
  ok: boolean;
  expires_in?: number;
  refreshed_at?: string;
  error?: string;
}> {
  const currentToken = await getActiveThreadsToken(env);
  if (!currentToken) {
    return { ok: false, error: "Missing THREADS_ACCESS_TOKEN" };
  }

  const refreshUrl = new URL("https://graph.threads.net/refresh_access_token");
  refreshUrl.searchParams.set("grant_type", "th_refresh_token");
  refreshUrl.searchParams.set("access_token", currentToken);

  const res = await fetch(refreshUrl.toString(), { method: "GET" });
  const data = (await res.json()) as {
    access_token?: string;
    token_type?: string;
    expires_in?: number;
    error?: { message?: string };
  };

  if (!res.ok || !data.access_token) {
    return {
      ok: false,
      error: data.error?.message ?? `Token refresh failed with HTTP ${res.status}`,
    };
  }

  const refreshedAt = new Date().toISOString();
  if (env.THREADS_KV) {
    await env.THREADS_KV.put(KV_TOKEN_KEY, data.access_token);
    await env.THREADS_KV.put(
      KV_TOKEN_META_KEY,
      JSON.stringify({
        refreshed_at: refreshedAt,
        expires_in: data.expires_in ?? 5184000,
        token_type: data.token_type ?? "bearer",
      })
    );
  }

  return {
    ok: true,
    expires_in: data.expires_in,
    refreshed_at: refreshedAt,
  };
}

async function syncAiTask(
  env: Env,
  params: {
    taskId?: string;
    contentId?: string;
    vertical?: string;
    ownerAgent?: string;
    status: "in_progress" | "completed" | "degraded" | "repairing" | "realigned";
    creationId?: string;
    threadsPostId?: string;
    sanitizedText?: string;
    mediaType?: "TEXT" | "IMAGE" | "VIDEO";
    imageUrl?: string | null;
    videoUrl?: string | null;
    linkAttachment?: string | null;
    errorMessage?: string;
  }
): Promise<string | null> {
  if (!env.SUPABASE_URL || !env.SUPABASE_SERVICE_ROLE_KEY) return params.taskId ?? null;

  const taskId = params.taskId ?? crypto.randomUUID();
  const now = new Date().toISOString();

  const record: Record<string, unknown> = {
    task_id: taskId,
    content_id: params.contentId ?? `threads_${taskId.slice(0, 8)}`,
    owner_agent: params.ownerAgent ?? "gemini_architect",
    vertical: params.vertical ?? "civic_oversight",
    status: params.status,
    updated_at: now,
    output_payload: {
      surface: "threads",
      account: "209media.connect",
      media_type: params.mediaType ?? "TEXT",
      creation_id: params.creationId ?? null,
      threads_post_id: params.threadsPostId ?? null,
      sanitized_text: params.sanitizedText ?? null,
      image_url: params.imageUrl ?? null,
      video_url: params.videoUrl ?? null,
      link_attachment: params.linkAttachment ?? null,
      error: params.errorMessage ?? null,
      recorded_at: now,
    },
  };

  try {
    const res = await fetch(`${env.SUPABASE_URL}/rest/v1/ai_tasks?on_conflict=task_id`, {
      method: "POST",
      headers: supabaseHeaders(env, "resolution=merge-duplicates,return=minimal"),
      body: JSON.stringify(record),
    });
    if (!res.ok) {
      console.error("Supabase ai_tasks sync failed:", res.status, await res.text());
    }
  } catch (err) {
    console.error("Supabase ai_tasks network error:", err);
  }

  return taskId;
}

async function logDiagnosticTrace(
  env: Env,
  trace: {
    taskId: string | null;
    contentId: string | null;
    step: string;
    httpStatus: number;
    rootCause: string;
    creationId?: string;
    rawPayload: unknown;
  }
): Promise<void> {
  if (!env.SUPABASE_URL || !env.SUPABASE_SERVICE_ROLE_KEY) return;

  const body = {
    trace_id: crypto.randomUUID(),
    task_id: trace.taskId,
    content_id: trace.contentId,
    worker_name: "cf_209_threads_webhook",
    owner_agent: "diagnostic_sentinel",
    surface: "threads",
    stage: trace.step,
    http_status: trace.httpStatus,
    root_cause: trace.rootCause,
    metadata: {
      creation_id: trace.creationId ?? null,
      payload: trace.rawPayload,
    },
    created_at: new Date().toISOString(),
  };

  try {
    const res = await fetch(`${env.SUPABASE_URL}/rest/v1/diagnostic_traces`, {
      method: "POST",
      headers: supabaseHeaders(env, "return=minimal"),
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      console.error("Supabase diagnostic_traces insert failed:", res.status, await res.text());
    }
  } catch (err) {
    console.error("Supabase diagnostic_traces network error:", err);
  }
}

async function logRepairAction(
  env: Env,
  entry: {
    taskId: string;
    contentId: string;
    actionTaken: string;
    previousCreationId?: string | null;
    newCreationId?: string | null;
    threadsPostId?: string | null;
    outcome: "realigned" | "failed";
    notes: string;
  }
): Promise<void> {
  if (!env.SUPABASE_URL || !env.SUPABASE_SERVICE_ROLE_KEY) return;

  const body = {
    repair_id: crypto.randomUUID(),
    task_id: entry.taskId,
    content_id: entry.contentId,
    owner_agent: "repair_surgeon",
    surface: "threads",
    action_taken: entry.actionTaken,
    outcome: entry.outcome,
    metadata: {
      previous_creation_id: entry.previousCreationId ?? null,
      new_creation_id: entry.newCreationId ?? null,
      threads_post_id: entry.threadsPostId ?? null,
      notes: entry.notes,
    },
    created_at: new Date().toISOString(),
  };

  try {
    const res = await fetch(`${env.SUPABASE_URL}/rest/v1/repair_logs`, {
      method: "POST",
      headers: supabaseHeaders(env, "return=minimal"),
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      console.error("Supabase repair_logs insert failed:", res.status, await res.text());
    }
  } catch (err) {
    console.error("Supabase repair_logs network error:", err);
  }
}

async function checkContainerStatus(
  containerId: string,
  accessToken: string
): Promise<{ status: string; errorMessage?: string }> {
  const statusUrl = new URL(`${THREADS_GRAPH_BASE}/${containerId}`);
  statusUrl.searchParams.set("fields", "status,error_message");
  statusUrl.searchParams.set("access_token", accessToken);

  const res = await fetch(statusUrl.toString(), { method: "GET" });
  const data = (await res.json()) as {
    status?: string;
    error_message?: string;
    error?: { message?: string };
  };

  if (!res.ok) {
    return {
      status: "ERROR",
      errorMessage: data.error?.message ?? `HTTP ${res.status}`,
    };
  }

  return {
    status: data.status ?? "UNKNOWN",
    errorMessage: data.error_message,
  };
}

async function waitForContainerReady(
  containerId: string,
  accessToken: string,
  maxAttempts = 6,
  delayMs = 5000
): Promise<void> {
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    const check = await checkContainerStatus(containerId, accessToken);

    if (check.status === "FINISHED" || check.status === "PUBLISHED") {
      return;
    }

    if (check.status === "ERROR" || check.status === "EXPIRED") {
      throw new Error(
        `Threads container ${containerId} failed with status ${check.status}: ${check.errorMessage ?? "No details"}`
      );
    }

    if (attempt < maxAttempts) {
      await new Promise((resolve) => setTimeout(resolve, delayMs));
    }
  }

  throw new Error(`Threads container ${containerId} timed out waiting for FINISHED status.`);
}

async function createThreadsContainer(
  env: Env,
  accessToken: string,
  params: {
    mediaType: "TEXT" | "IMAGE" | "VIDEO";
    cleanText: string;
    imageUrl?: string;
    videoUrl?: string;
    linkAttachment?: string;
    topicTag?: string;
    replyToId?: string;
    isMadeWithAi?: boolean;
  }
): Promise<{ ok: boolean; creationId?: string; status: number; error?: string }> {
  const createParams = new URLSearchParams();
  createParams.set("media_type", params.mediaType);
  createParams.set("text", params.cleanText);
  createParams.set("access_token", accessToken);

  if (params.mediaType === "IMAGE") {
    if (!params.imageUrl) {
      return { ok: false, status: 400, error: "image_url is required when media_type is IMAGE" };
    }
    createParams.set("image_url", params.imageUrl);
  } else if (params.mediaType === "VIDEO") {
    if (!params.videoUrl) {
      return { ok: false, status: 400, error: "video_url is required when media_type is VIDEO" };
    }
    createParams.set("video_url", params.videoUrl);
  } else if (params.linkAttachment) {
    createParams.set("link_attachment", params.linkAttachment);
  }

  if (params.topicTag) createParams.set("topic_tag", sanitizeCopy(params.topicTag));
  if (params.replyToId) createParams.set("reply_to_id", params.replyToId);
  if (params.isMadeWithAi) createParams.set("is_made_with_ai", "true");

  const createRes = await fetch(
    `${THREADS_GRAPH_BASE}/${encodeURIComponent(env.THREADS_USER_ID)}/threads`,
    {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: createParams.toString(),
    }
  );

  const createData = (await createRes.json()) as {
    id?: string;
    error?: { message?: string };
  };

  if (!createRes.ok || !createData.id) {
    return {
      ok: false,
      status: createRes.status,
      error: createData.error?.message ?? "Failed to create Threads container",
    };
  }

  return { ok: true, creationId: createData.id, status: createRes.status };
}

async function publishThreadsContainer(
  env: Env,
  accessToken: string,
  creationId: string
): Promise<{ ok: boolean; threadsPostId?: string; status: number; error?: string }> {
  const publishParams = new URLSearchParams();
  publishParams.set("creation_id", creationId);
  publishParams.set("access_token", accessToken);

  const publishRes = await fetch(
    `${THREADS_GRAPH_BASE}/${encodeURIComponent(env.THREADS_USER_ID)}/threads_publish`,
    {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: publishParams.toString(),
    }
  );

  const publishData = (await publishRes.json()) as {
    id?: string;
    error?: { message?: string };
  };

  if (!publishRes.ok || !publishData.id) {
    return {
      ok: false,
      status: publishRes.status,
      error: publishData.error?.message ?? "Failed to publish Threads container",
    };
  }

  return { ok: true, threadsPostId: publishData.id, status: publishRes.status };
}

function authorizeCaller(request: Request, env: Env): boolean {
  const authHeader = request.headers.get("Authorization") ?? "";
  return Boolean(env.ZAPIER_WEBHOOK_SECRET) && authHeader === `Bearer ${env.ZAPIER_WEBHOOK_SECRET}`;
}

/**
 * Primary Webhook Entrypoint: POST /webhooks/threads
 */
export async function handleThreadsWebhook(
  request: Request,
  env: Env,
  ctx?: ExecutionContext
): Promise<Response> {
  if (request.method !== "POST") {
    return Response.json({ ok: false, error: "Method not allowed" }, { status: 405 });
  }

  if (!authorizeCaller(request, env)) {
    return Response.json({ ok: false, error: "Unauthorized webhook caller" }, { status: 401 });
  }

  let payload: ZapierThreadsPayload;
  try {
    payload = (await request.json()) as ZapierThreadsPayload;
  } catch {
    return Response.json({ ok: false, error: "Invalid JSON payload" }, { status: 400 });
  }

  if (!payload.text || typeof payload.text !== "string") {
    return Response.json({ ok: false, error: "Missing required field: text" }, { status: 400 });
  }

  const track = (promise: Promise<unknown>) => {
    if (ctx && typeof ctx.waitUntil === "function") {
      ctx.waitUntil(promise);
      return Promise.resolve();
    }
    return promise;
  };

  let activeTaskId: string | null = payload.task_id ?? crypto.randomUUID();
  let creationId: string | undefined;
  let currentStep = "sanitize_and_validate";

  try {
    const cleanText = sanitizeCopy(payload.text);
    assertThreadsByteLimit(cleanText, 500);

    const mediaType =
      payload.media_type ?? (payload.video_url ? "VIDEO" : payload.image_url ? "IMAGE" : "TEXT");
    const accessToken = await getActiveThreadsToken(env);

    activeTaskId = await syncAiTask(env, {
      taskId: activeTaskId,
      contentId: payload.content_id,
      vertical: payload.vertical,
      status: "in_progress",
      sanitizedText: cleanText,
      mediaType,
      imageUrl: payload.image_url ?? null,
      videoUrl: payload.video_url ?? null,
      linkAttachment: payload.link_attachment ?? null,
    });

    // Step 1: Create Container
    currentStep = "create_container";
    const created = await createThreadsContainer(env, accessToken, {
      mediaType,
      cleanText,
      imageUrl: payload.image_url,
      videoUrl: payload.video_url,
      linkAttachment: payload.link_attachment,
      topicTag: payload.topic_tag,
      replyToId: payload.reply_to_id,
      isMadeWithAi: payload.is_made_with_ai,
    });

    if (!created.ok || !created.creationId) {
      const rootCause = created.error ?? "Container creation failed";
      await track(
        Promise.all([
          syncAiTask(env, {
            taskId: activeTaskId ?? undefined,
            contentId: payload.content_id,
            vertical: payload.vertical,
            status: "degraded",
            sanitizedText: cleanText,
            mediaType,
            errorMessage: rootCause,
          }),
          logDiagnosticTrace(env, {
            taskId: activeTaskId,
            contentId: payload.content_id ?? null,
            step: currentStep,
            httpStatus: created.status,
            rootCause,
            rawPayload: payload,
          }),
        ])
      );

      return Response.json(
        { ok: false, task_id: activeTaskId, step: currentStep, status: created.status, error: rootCause },
        { status: 502 }
      );
    }

    creationId = created.creationId;

    // Persist creation_id immediately for repair_surgeon recovery
    await syncAiTask(env, {
      taskId: activeTaskId ?? undefined,
      contentId: payload.content_id,
      vertical: payload.vertical,
      status: "in_progress",
      creationId,
      sanitizedText: cleanText,
      mediaType,
      imageUrl: payload.image_url ?? null,
      videoUrl: payload.video_url ?? null,
      linkAttachment: payload.link_attachment ?? null,
    });

    if (mediaType === "IMAGE" || mediaType === "VIDEO") {
      currentStep = "poll_container_status";
      await waitForContainerReady(creationId, accessToken);
    }

    // Step 2: Publish Container
    currentStep = "publish_container";
    const published = await publishThreadsContainer(env, accessToken, creationId);

    if (!published.ok || !published.threadsPostId) {
      const rootCause = published.error ?? "Container publish failed";
      await track(
        Promise.all([
          syncAiTask(env, {
            taskId: activeTaskId ?? undefined,
            contentId: payload.content_id,
            vertical: payload.vertical,
            status: "degraded",
            creationId,
            sanitizedText: cleanText,
            mediaType,
            errorMessage: rootCause,
          }),
          logDiagnosticTrace(env, {
            taskId: activeTaskId,
            contentId: payload.content_id ?? null,
            step: currentStep,
            httpStatus: published.status,
            rootCause,
            creationId,
            rawPayload: payload,
          }),
        ])
      );

      return Response.json(
        {
          ok: false,
          task_id: activeTaskId,
          step: currentStep,
          creation_id: creationId,
          status: published.status,
          error: rootCause,
        },
        { status: 502 }
      );
    }

    await track(
      syncAiTask(env, {
        taskId: activeTaskId ?? undefined,
        contentId: payload.content_id,
        vertical: payload.vertical,
        status: "completed",
        creationId,
        threadsPostId: published.threadsPostId,
        sanitizedText: cleanText,
        mediaType,
      })
    );

    return Response.json({
      ok: true,
      task_id: activeTaskId,
      content_id: payload.content_id ?? null,
      media_type: mediaType,
      creation_id: creationId,
      threads_post_id: published.threadsPostId,
      sanitized_text: cleanText,
    });
  } catch (err) {
    const rootCause = err instanceof Error ? err.message : "Unexpected Threads relay error";
    await track(
      Promise.all([
        syncAiTask(env, {
          taskId: activeTaskId ?? undefined,
          contentId: payload.content_id,
          vertical: payload.vertical,
          status: "degraded",
          creationId,
          errorMessage: rootCause,
        }),
        logDiagnosticTrace(env, {
          taskId: activeTaskId,
          contentId: payload.content_id ?? null,
          step: currentStep,
          httpStatus: 500,
          rootCause,
          creationId,
          rawPayload: payload,
        }),
      ])
    );

    return Response.json(
      { ok: false, task_id: activeTaskId, step: currentStep, creation_id: creationId ?? null, error: rootCause },
      { status: 500 }
    );
  }
}

/**
 * Repair Surgeon Retry Endpoint: POST /repair/threads
 * Reads degraded Threads tasks from publishing_209.ai_tasks.
 * If a valid creation_id already exists, resumes directly at threads_publish.
 * If creation_id is missing or expired, rebuilds the container and publishes cleanly.
 */
export async function handleThreadsRepairRetry(
  request: Request,
  env: Env
): Promise<Response> {
  if (request.method !== "POST") {
    return Response.json({ ok: false, error: "Method not allowed" }, { status: 405 });
  }

  if (!authorizeCaller(request, env)) {
    return Response.json({ ok: false, error: "Unauthorized repair caller" }, { status: 401 });
  }

  let body: RepairRetryPayload = {};
  try {
    body = (await request.json()) as RepairRetryPayload;
  } catch {
    body = {};
  }

  const limit = Math.min(Math.max(body.limit ?? 10, 1), 25);
  const queryUrl = new URL(`${env.SUPABASE_URL}/rest/v1/ai_tasks`);
  queryUrl.searchParams.set("status", "eq.degraded");
  queryUrl.searchParams.set("output_payload->>surface", "eq.threads");
  queryUrl.searchParams.set("order", "updated_at.asc");
  queryUrl.searchParams.set("limit", String(limit));
  if (body.task_id) {
    queryUrl.searchParams.set("task_id", `eq.${body.task_id}`);
  }

  const fetchTasksRes = await fetch(queryUrl.toString(), {
    method: "GET",
    headers: supabaseHeaders(env),
  });

  if (!fetchTasksRes.ok) {
    const errText = await fetchTasksRes.text();
    return Response.json(
      { ok: false, error: `Failed to fetch degraded tasks: ${fetchTasksRes.status} ${errText}` },
      { status: 502 }
    );
  }

  const tasks = (await fetchTasksRes.json()) as AiTaskRow[];
  const accessToken = await getActiveThreadsToken(env);
  const results: Array<Record<string, unknown>> = [];

  for (const task of tasks) {
    const out = task.output_payload ?? {};
    const savedCreationId = out.creation_id ?? null;
    const rawText = out.sanitized_text ?? "";
    const cleanText = sanitizeCopy(rawText);
    const mediaType = out.media_type ?? "TEXT";

    await syncAiTask(env, {
      taskId: task.task_id,
      contentId: task.content_id,
      vertical: task.vertical,
      ownerAgent: "repair_surgeon",
      status: "repairing",
      creationId: savedCreationId ?? undefined,
      sanitizedText: cleanText,
      mediaType,
    });

    let activeCreationId = savedCreationId;
    let actionTaken = "resume_publish_existing_container";

    // Verify if existing container is still valid and publishable
    if (activeCreationId) {
      const statusCheck = await checkContainerStatus(activeCreationId, accessToken);
      if (statusCheck.status === "EXPIRED" || statusCheck.status === "ERROR") {
        activeCreationId = null;
      } else if (statusCheck.status === "IN_PROGRESS") {
        await waitForContainerReady(activeCreationId, accessToken);
      }
    }

    // Rebuild container if none exists or previous container expired
    if (!activeCreationId) {
      if (!cleanText) {
        await logRepairAction(env, {
          taskId: task.task_id,
          contentId: task.content_id,
          actionTaken: "abort_empty_text",
          previousCreationId: savedCreationId,
          outcome: "failed",
          notes: "Cannot rebuild container without stored text.",
        });
        results.push({ task_id: task.task_id, ok: false, error: "Empty text in degraded task" });
        continue;
      }

      actionTaken = "rebuild_container_and_publish";
      const recreated = await createThreadsContainer(env, accessToken, {
        mediaType,
        cleanText,
        imageUrl: out.image_url ?? undefined,
        videoUrl: out.video_url ?? undefined,
        linkAttachment: out.link_attachment ?? undefined,
      });

      if (!recreated.ok || !recreated.creationId) {
        const reason = recreated.error ?? "Container rebuild failed";
        await syncAiTask(env, {
          taskId: task.task_id,
          contentId: task.content_id,
          vertical: task.vertical,
          ownerAgent: "repair_surgeon",
          status: "degraded",
          sanitizedText: cleanText,
          mediaType,
          errorMessage: reason,
        });
        await logRepairAction(env, {
          taskId: task.task_id,
          contentId: task.content_id,
          actionTaken,
          previousCreationId: savedCreationId,
          outcome: "failed",
          notes: reason,
        });
        results.push({ task_id: task.task_id, ok: false, step: "rebuild_container", error: reason });
        continue;
      }

      activeCreationId = recreated.creationId;
      if (mediaType === "IMAGE" || mediaType === "VIDEO") {
        await waitForContainerReady(activeCreationId, accessToken);
      }
    }

    // Execute Step 2 publish
    const published = await publishThreadsContainer(env, accessToken, activeCreationId);
    if (!published.ok || !published.threadsPostId) {
      const reason = published.error ?? "Repair publish failed";
      await syncAiTask(env, {
        taskId: task.task_id,
        contentId: task.content_id,
        vertical: task.vertical,
        ownerAgent: "repair_surgeon",
        status: "degraded",
        creationId: activeCreationId,
        sanitizedText: cleanText,
        mediaType,
        errorMessage: reason,
      });
      await logRepairAction(env, {
        taskId: task.task_id,
        contentId: task.content_id,
        actionTaken,
        previousCreationId: savedCreationId,
        newCreationId: activeCreationId,
        outcome: "failed",
        notes: reason,
      });
      results.push({
        task_id: task.task_id,
        ok: false,
        step: "publish_container",
        creation_id: activeCreationId,
        error: reason,
      });
      continue;
    }

    // Transition task to completed & log successful realignment
    await syncAiTask(env, {
      taskId: task.task_id,
      contentId: task.content_id,
      vertical: task.vertical,
      ownerAgent: "repair_surgeon",
      status: "completed",
      creationId: activeCreationId,
      threadsPostId: published.threadsPostId,
      sanitizedText: cleanText,
      mediaType,
    });

    await logRepairAction(env, {
      taskId: task.task_id,
      contentId: task.content_id,
      actionTaken,
      previousCreationId: savedCreationId,
      newCreationId: activeCreationId,
      threadsPostId: published.threadsPostId,
      outcome: "realigned",
      notes: "Threads post published and state realigned in publishing_209.ai_tasks.",
    });

    results.push({
      task_id: task.task_id,
      ok: true,
      action_taken: actionTaken,
      creation_id: activeCreationId,
      threads_post_id: published.threadsPostId,
    });
  }

  return Response.json({
    ok: true,
    processed_count: results.length,
    results,
  });
}

/**
 * Manual or Scheduled Token Rotation Entrypoint: POST /auth/threads/refresh
 */
export async function handleThreadsTokenRefreshRoute(
  request: Request,
  env: Env
): Promise<Response> {
  if (request.method !== "POST") {
    return Response.json({ ok: false, error: "Method not allowed" }, { status: 405 });
  }
  if (!authorizeCaller(request, env)) {
    return Response.json({ ok: false, error: "Unauthorized caller" }, { status: 401 });
  }
  const result = await refreshThreadsAccessToken(env);
  return Response.json(result, { status: result.ok ? 200 : 502 });
}
