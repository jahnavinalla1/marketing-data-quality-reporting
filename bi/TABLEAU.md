# Tableau dashboard build guide

Status: CSV exports and exact build specifications supplied; no Tableau workbook has been created or published. Build these in Tableau Desktop/Public after regenerating data. Every workbook title must include “Synthetic portfolio study.”

## 04 — Reporting

Connect to `outputs/daily_marketing.csv`. Reuse ratio-of-sums Media CAC. Create daily acquisition and CAC trends by channel. Add `outputs/quality_checks.csv` separately for a colored PASS/WARN/FAIL table, and `outputs/quarantine.csv` for excluded member IDs/reasons. Show fixed as-of date and partial-week caveat. No member-level joins to spend. Reconcile SUM(spend_usd) and SUM(new_members) to the SQL marts.

## Validation before publishing

Check each dashboard's full-data totals, one filtered slice, zero-denominator behavior, field types, tooltips, and synthetic-data disclosure. Export a screenshot, retain the `.twb`/`.twbx`, and add a real Tableau Public URL only after publishing. Never place real customer IDs in a public workbook.
