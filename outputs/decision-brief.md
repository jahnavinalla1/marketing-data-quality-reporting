# Trusted Marketing Data & Weekly Reporting

> Independent, AI-assisted portfolio study. All data are synthetic.

## Decision brief

- Joining raw member events directly to daily spend would inflate spend by 15.3×. Aggregate facts to date/campaign grain before joining.
- Deduplicate 12 replayed ingestions, exclude one invalid revenue record, and quarantine one unmapped acquisition. Report warnings visibly rather than silently losing records.
- The clean mart reconciles to source spend and eligible distinct members. Release with disclosed warnings; route unmapped campaigns to Marketing Operations and invalid amounts to the source owner.
- Freshness is evaluated against the fixed simulation as-of date 2026-09-29. The recurring run must use a production as-of parameter and an agreed ingestion SLA.

## Results

| Metric | Value |
|---|---|
| Duplicate replays | 12 |
| Quarantined members | 2 |
| Blocking failures | 0 |
| Naive join inflation | 15.3× |

## Interpretation limits

Synthetic ingestion exercise. One row per member represents one acquisition; this is not a full order ledger. Raw inputs deliberately include known defects. WARN checks overlap and must not be summed as distinct incidents. Nonnegative net receipts are required by this acquisition contract; refund transactions need a separate ledger. Media spend is USD and timestamps are UTC. The final week is partial, so do not compare unadjusted weekly totals. No live platform connector or scheduled production job is deployed.

## Review with Growth Marketing

Confirm the decision, measurement window, constraints, and alternative explanations before acting. Document feedback and rerun the analysis when assumptions change.

Open `dashboard.html` locally for interactive charts and tables. `results.json` is the exact report input.
