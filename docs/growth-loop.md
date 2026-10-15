# Growth Loop — Adaptive Digest

## Direction of flow

- Muse → data/signals.json: post performance, CTA results, format results, timing results, audience signals.
- Intelligence → data/decisions.json: CTA/format/timing/mission/volume directives back to Muse.
- Both → data/experiments.json: active A/B tests and results.

## Adaptive digestion

data/digest.json controls WHEN the intelligence layer digests signals:

- base_interval_min: 240 — normal digestion every 4 hours.
- fast_interval_min: 60 — digest hourly when a fast trigger is active.
- best_times: 09:00, 12:00, 17:00 PT — always digest at these windows regardless of interval.
- fast_triggers: open_incident, cadence_breach, queue_starvation, viral_post.

## Next-digest logic

next_digest = min(next best_time, last_digest + active_interval)

where active_interval = fast_interval_min if any fast trigger is active, else base_interval_min.

Muse (or a cron) should:
1. Read signals + incidents + pipeline.
2. Compute next_digest and next_digest_reason.
3. Write both back to digest.json.
4. At digest time: interpret signals, write directives to decisions.json, update experiments.json.

## Directive schema (decisions.json)

{ date, type: CTA|FORMAT|TIMING|MISSION|VOLUME|EXPERIMENT, target_lane, directive, reason, expires }

## Signal schema (signals.json)

posts: [{ date, lane, post_id, format, cta_variant, time_slot, impressions, engagement, clicks, saves, replies }]
cta_results: [{ date, lane, variant, softness, clicks, subs }]
format_results: [{ date, lane, format, engagement_rate }]
timing_results: [{ date, lane, time_slot, engagement_rate }]
audience_signals: [{ date, lane, follower_quality, reply_sentiment }]

## Experiment schema (experiments.json)

{ id, started, lane, metric, variants: [{name, result}], winner, status }
