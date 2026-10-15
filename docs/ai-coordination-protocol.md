# AI Coordination Protocol — 209 Media

## Purpose
Enable the 3 AIs (Muse, 209 Intelligence/site agent, and the third AI) to communicate, share state, self-guide, and enforce protection protocols — using the GitHub repo as a shared blackboard.

## Current state (before this protocol)
- Muse WRITES data files (analytics, calendar, shift, pipeline, incidents, muse-morning).
- The site READS those files and renders them.
- Result: one-way (Muse → site). No pull, no inter-AI messaging, no shared decision state.

## Target state (two-way blackboard)

```text
MUSE (writer/reader)  ←→  data/coordination.json  ←→  SITE AGENT (reader/writer)
                              ↑↓
                        THIRD AI (reader/writer)
```

All three AIs read and write to `data/coordination.json` using a strict schema. GitHub is the source of truth; each AI polls or is triggered on commit.

## coordination.json schema

```json
{
  "version": 1,
  "updated_at": "ISO timestamp",
  "ais": {
    "muse": { "status": "ACTIVE", "last_heartbeat": "...", "current_task": "..." },
    "intelligence": { "status": "ACTIVE", "last_heartbeat": "...", "current_task": "..." },
    "third_ai": { "status": "ACTIVE", "last_heartbeat": "...", "current_task": "..." }
  },
  "messages": [
    {
      "id": "msg-001",
      "from": "muse",
      "to": "intelligence",
      "type": "ALERT" | "REQUEST" | "UPDATE" | "DECISION",
      "priority": "HIGH" | "MEDIUM" | "LOW",
      "subject": "...",
      "body": "...",
      "requires_action": true,
      "status": "NEW" | "ACKNOWLEDGED" | "RESOLVED",
      "created_at": "..."
    }
  ],
  "shared_state": {
    "queue_health": { "lane": "staged_count" },
    "active_incidents": [],
    "first_shift": { "status": "ARMED" },
    "protection_locks": []
  },
  "protection": {
    "human_approval_required": ["spend_money", "delete_data", "publish_sensitive"],
    "rate_limits": { "max_messages_per_hour": 50 },
    "conflict_rule": "last_writer_wins_with_lock"
  }
}
```

## Communication rules

1. **Message types**: ALERT (something broke), REQUEST (need the other AI to act), UPDATE (FYI state change), DECISION (proposed action needing ack).
2. **Addressing**: `to` can be a specific AI or `"all"`.
3. **Acknowledgment**: receiving AI sets status to ACKNOWLEDGED, then RESOLVED after acting.
4. **Heartbeats**: each AI updates its own `ais.<name>` block every cycle.
5. **Conflict safety**: use a lock key in `protection.locks` before writing shared_state; stale locks auto-expire after 5 minutes.

## Self-guidance loop

```text
Muse detects cadence breach
  → writes ALERT to coordination.json
  → Intelligence reads it, updates dashboard + recommendations
  → Intelligence writes DECISION back (e.g., "boost TikTok priority")
  → Muse reads decision, adjusts next dispatch cycle
  → Result feeds analytics → next cycle is smarter
```

## Protection protocols

1. **Human approval gate**: any action in `human_approval_required` list needs a message to the human and cannot auto-execute.
2. **Rate limits**: max 50 messages/hour per AI to prevent runaway loops.
3. **Write validation**: all writes to coordination.json must validate against the schema; invalid writes are rejected.
4. **Lock before shared-state writes**: prevents two AIs from clobbering each other.
5. **Audit trail**: every message is immutable once written; corrections are new messages, not edits.
6. **Kill switch**: human can set `protection.kill_switch: true` — all AIs pause non-essential actions.

## Implementation notes

- Muse reads/writes via GitHub Contents API (or a thin worker using the GitHub MCP).
- Site agent reads coordination.json on the same 5-min refresh cycle as other feeds.
- Third AI integrates the same way — read/write coordination.json, respect locks and approval gates.
