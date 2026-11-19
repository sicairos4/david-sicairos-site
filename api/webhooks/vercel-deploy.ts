export const config = {
  runtime: "edge",
};

async function verifyVercelSignature(
  rawBody: string,
  signatureHeader: string | null,
  secret: string
): Promise<boolean> {
  if (!signatureHeader || !secret) return false;
  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw",
    encoder.encode(secret),
    { name: "HMAC", hash: "SHA-1" },
    false,
    ["sign"]
  );
  const signatureBuffer = await crypto.subtle.sign(
    "HMAC",
    key,
    encoder.encode(rawBody)
  );
  const computedHex = Array.from(new Uint8Array(signatureBuffer))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
  return computedHex === signatureHeader;
}

export default async function handler(req: Request): Promise<Response> {
  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "Method not allowed" }), {
      status: 405,
      headers: { "Content-Type": "application/json" },
    });
  }

  const rawBody = await req.text();
  const signature = req.headers.get("x-vercel-signature");
  const webhookSecret = process.env.VERCEL_WEBHOOK_SECRET ?? "";

  const isValid = await verifyVercelSignature(rawBody, signature, webhookSecret);
  if (!isValid) {
    return new Response(JSON.stringify({ error: "Invalid Vercel signature" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });
  }

  const event = JSON.parse(rawBody);
  const eventType: string = event?.type ?? "unknown";

  if (eventType !== "deployment.error" && eventType !== "deployment.canceled") {
    return new Response(
      JSON.stringify({ ok: true, ignored_event: eventType }),
      { status: 200, headers: { "Content-Type": "application/json" } }
    );
  }

  const deployment = event?.payload?.deployment ?? {};
  const failedSha: string = deployment?.meta?.githubCommitSha ?? "unknown";
  const projectName: string = deployment?.name ?? "david-sicairos-site";
  const deploymentId: string = deployment?.id ?? crypto.randomUUID();
  const taskId = crypto.randomUUID();

  const githubToken = process.env.GITHUB_PAT ?? "";
  const repoOwner = "sicairos4";
  const repoName = "david-sicairos-site";
  let rollbackStatus = "skipped_missing_token";

  if (githubToken) {
    const commitsRes = await fetch(
      `https://api.github.com/repos/${repoOwner}/${repoName}/commits?sha=main&per_page=5`,
      {
        headers: {
          Authorization: `Bearer ${githubToken}`,
          Accept: "application/vnd.github+json",
          "User-Agent": "209-vercel-rollback-sentinel",
        },
      }
    );

    if (commitsRes.ok) {
      const commits = (await commitsRes.json()) as Array<{ sha: string }>;
      const previousGreenCommit = commits.find((c) => c.sha !== failedSha);

      if (previousGreenCommit) {
        const issueRes = await fetch(
          `https://api.github.com/repos/${repoOwner}/${repoName}/issues`,
          {
            method: "POST",
            headers: {
              Authorization: `Bearer ${githubToken}`,
              Accept: "application/vnd.github+json",
              "Content-Type": "application/json",
              "User-Agent": "209-vercel-rollback-sentinel",
            },
            body: JSON.stringify({
              title: `Auto Rollback Alert: Vercel deployment ${deploymentId} failed`,
              body: [
                `Project: ${projectName}`,
                `Failed Commit SHA: ${failedSha}`,
                `Target Green Rollback SHA: ${previousGreenCommit.sha}`,
                `Triad Task ID: ${taskId}`,
                `Action: diagnostic_sentinel dispatched trace to cf-209-worker.`,
              ].join("\n"),
              labels: ["triad-rollback", "automated"],
            }),
          }
        );
        rollbackStatus = issueRes.ok
          ? `logged_rollback_target_${previousGreenCommit.sha.slice(0, 7)}`
          : `github_issue_error_${issueRes.status}`;
      }
    }
  }

  const cfRouterUrl = process.env.CF_209_WORKER_URL ?? "";
  const cfBearer = process.env.WORKER_BEARER_TOKEN ?? "";

  if (cfRouterUrl && cfBearer) {
    await fetch(`${cfRouterUrl}/mesh/diagnose`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${cfBearer}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        task_id: taskId,
        content_id: `vercel-deploy-${deploymentId}`,
        owner_agent: "diagnostic_sentinel",
        hop_count: 1,
        max_hops: 5,
        vertical: "personal_apex",
        verified_evidence: [deployment?.url ?? "https://vercel.com"],
        status: "degraded",
        payload: {
          project: projectName,
          failed_sha: failedSha,
          rollback_status: rollbackStatus,
        },
        error_context: {
          http_status: 500,
          error_code: eventType.toUpperCase(),
          message: `Vercel deployment ${eventType} on commit ${failedSha}`,
          failed_agent: "gemini_architect",
        },
      }),
    });
  }

  return new Response(
    JSON.stringify({
      ok: true,
      task_id: taskId,
      rollback_status: rollbackStatus,
    }),
    { status: 200, headers: { "Content-Type": "application/json" } }
  );
}