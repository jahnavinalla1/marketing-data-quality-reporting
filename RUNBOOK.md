# Recurring report runbook

This repository implements a local repeatable simulation, not a live scheduler.

1. Regenerate the demonstration with `python3 run.py`. Production adaptation should instead ingest immutable source extracts for a declared as-of date.
2. Validate campaign/spend keys, nonnegative spend, mapping coverage, and freshness before release. The code raises on any blocking failure.
3. Rank member events by business ID and ingestion time. Keep one acquisition record per member; quarantine invalid receipts and missing spend keys.
4. Aggregate member facts to date/campaign and join to unique daily spend. Reconcile spend and eligible member counts.
5. Inspect warning details; warning counts can overlap. In this dataset, 12 replays are corrected and two records are quarantined.
6. Publish the daily/weekly CSVs and brief only after gates pass. Include warning counts, as-of date, and partial-week status. A production release should atomically swap the last-known-good mart.
7. Review weekly with Growth Marketing; track questions and corrections in a dated log. This proposed review has not occurred.

Failure response: preserve the last good report, capture the failed check and source batch, notify the responsible owner through an approved workflow, repair mapping/source data, rerun, reconcile, and record the resolution. This project does not send notifications automatically.
