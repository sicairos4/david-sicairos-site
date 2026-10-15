# Adaptation Feed Worker Contract

Muse/Gemini writes one row to `adaptation_log` per decision cycle:

```json
{
  "trigger": "Engagement spike / Breaking news / Underperformance",
  "observation": "Threads post X engagement +38% in 2h",
  "decision": "Shift to breaking-news hooks",
  "action": "Adjusted next 3 posts; moved window 45 min earlier",
  "status": "Applied",
  "platform": "Threads",
  "post_url": "https://..."
}
```

Top posts are written to `top_posts_48h` from GA4 every 15 min:

```json
{
  "title": "Post title",
  "platform": "Threads",
  "engagement_delta": 38.0,
  "reason": "Breaking news spike",
  "url": "https://..."
}
```

Run `node worker/adaptation-cycle.js` on a 15-min GitHub Actions cron or always-on worker.