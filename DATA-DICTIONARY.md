# Data contracts and metric definitions

All records are synthetic. Seeds 41, 52, 63, and 74 regenerate the four respective datasets. No personal data, WHOOP data, scraped ad accounts, or API credentials are used.

## Project 04 — reporting reliability

`campaigns.csv`: one row per campaign. `spend_daily.csv`: unique date × campaign spend. `raw_members.csv`: ingestion events for acquisitions; member IDs can repeat on replay. Latest `ingested_at`, then greatest `ingestion_id`, wins. All dates are UTC. The reporting window is September 1–28, 2026, with fixed as-of September 29.

Deduplicated acquisitions with nonnegative receipts enter `valid_members`. Acquisitions without a spend key are separately quarantined. Aggregating acquisition facts before joining prevents spend fanout. `daily_marketing.csv` is the portable BI fact; `weekly_marketing.csv` is a presentation aggregate, and its final week is partial. Freshness passes within one day. All blocker checks must pass; warning checks disclose known quarantines/replays. Warning counts overlap and are not additive.

Production adaptation requires real ingestion contracts, approved attribution windows, campaign mapping ownership, FX normalization, late-arrival handling, privacy review for real identifiers, and separate refund/subscription ledgers. These are future integration needs, not implemented platform connections.
