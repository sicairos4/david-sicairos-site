# Brand & Data Fabric — Connecting All Brands, Assets, and Backends

## The problem it solves

Today each brand (209 Media, 209 Connect, 209 Audit, dBeastco, Systems Studio, Sovereign University, David Sicairos personal) has its own pages, data feeds, and audiences — but they don't share what they learn. This blueprint connects them so every brand's wins upgrade every other brand.

## 1. Brand Registry (single source of truth)

One file defines every brand, so all systems agree on identity:

`data/brands.json`

```json
{
  "brands": [
    {
      "id": "209-media",
      "name": "209 Media",
      "role": "alternative media / accountability",
      "voice": "founder-led, receipt-driven, civic",
      "audience": "Central Valley civic-minded readers",
      "entry_page": "/",
      "color": "#1a7f37",
      "lanes": ["threads", "bluesky", "linkedin"]
    },
    {
      "id": "dbeastco",
      "name": "dBeastco Wellness",
      "role": "wellness product ecosystem",
      "voice": "performance, practical, founder-tested",
      "audience": "wellness/performance seekers",
      "entry_page": "/dbeastco.html",
      "color": "#4BDAF3",
      "lanes": ["ig", "tiktok", "youtube"]
    }
  ]
}
```

Every post, page, CTA, and experiment is tagged with a `brand_id` — this is what makes cross-brand learning possible.

## 2. Shared identity layer (branding + website)

- **Design tokens**: one `tokens.css` (colors, fonts, spacing) that every site imports; brand overrides via `data-brand` attribute.
- **Component library**: shared nav, cards, CTAs, footers — one update upgrades every brand's site.
- **Cross-linking rules**: every brand page exposes the others at the right moment (209 Audit reader → 209 Connect invite; dBeastco buyer → Systems Studio). No random cross-promotion — rule-based, context-aware.
- **Canonical identity**: one favicon/logo system, one OG image template, consistent authorship (David Sicairos) across all properties.

## 3. Shared event spine (backends that talk)

Every asset — post, page, email, product — emits events into one warehouse (Supabase), with a common schema:

```json
{
  "event": "engage" | "click" | "subscribe" | "purchase" | "publish",
  "brand_id": "209-media",
  "asset_id": "post-123",
  "lane": "linkedin",
  "mission": "records-wave",
  "cta_variant": "soft-2",
  "ts": "2026-10-15T12:00:00Z",
  "metrics": { "impressions": 0, "engagements": 0, "clicks": 0 }
}
```

Because every event carries `brand_id`, the intelligence layer can answer cross-brand questions:

- Which CTA style works across ALL brands vs brand-specific?
- Does a 209 Audit reader who clicks also convert on 209 Connect?
- Which dBeastco format learnings transfer to 209 Media video?

## 4. Cross-brand learning (how they upgrade each other)

The intelligence layer runs three learning loops:

1. **Within-brand**: lane-level optimization (already built — signals → decisions).
2. **Cross-brand transfer**: when a pattern wins in one brand (e.g., short receipt-style hooks), test it in adjacent brands with a tagged experiment — only promote if it wins there too.
3. **Ecosystem-level**: audience overlap analysis — find which brand is the best entry point for each audience segment, and route cross-links accordingly.

Rule: **learn locally, transfer deliberately, verify before promoting.** A win in dBeastco is a hypothesis for 209 Media, not a directive.

## 5. Social research agent (always learning)

A scheduled research job keeps the system current on platform behavior:

- **Cadence**: weekly deep research + daily light checks.
- **Inputs**: platform algorithm updates, format trend reports, posting-time studies, competitor/creator pattern analysis.
- **Output**: `data/research.json` — dated findings with source, confidence, and recommended test.
- **Integration**: research findings become tagged experiments in `experiments.json`; only experiments that win become playbooks.

```json
{
  "date": "2026-10-15",
  "platform": "linkedin",
  "finding": "document-style posts showing higher dwell time this month",
  "source": "platform trend report",
  "confidence": "medium",
  "recommended_test": "test document-format on 209 Audit lane for 2 weeks"
}
```

## 6. Self-upgrading loop (how the system improves itself)

```text
Research agent → new hypothesis
        ↓
Experiment engine → tagged test runs on one lane/brand
        ↓
Signals → result measured
        ↓
Intelligence → winner? promote to playbook : discard
        ↓
Playbook update → Muse's next posts improve
        ↻ repeat
```

- `data/playbooks.json` — versioned best practices per platform/brand (what's proven, not what's trendy).
- Every playbook entry cites the experiment that proved it.
- Playbook changes ship as small, reviewable updates — Muse proposes, David approves material changes.

## 7. Governance

- **One identity, many brands**: David Sicairos is the connective tissue; each brand keeps a distinct voice and audience.
- **Consent boundaries**: no cross-brand data use beyond aggregate patterns; personal data stays segmented.
- **Change control**: playbook/directive changes that alter brand voice or cross-linking require David's approval; pure performance tuning is autonomous.

## Build order

1. `data/brands.json` — brand registry (Muse + David define once).
2. Tag all existing events/feeds with `brand_id`.
3. Shared `tokens.css` + component pass across sites.
4. Research agent cron → `data/research.json`.
5. Cross-brand experiment tagging in `experiments.json`.
6. `data/playbooks.json` + promotion rules.
