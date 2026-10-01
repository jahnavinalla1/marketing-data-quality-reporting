# Looker source — Trusted Marketing Data & Reporting

Native LookML source is included in this folder. It has not been deployed or validated in a Looker tenant. The HTML report in `outputs/` is the immediately runnable dashboard.

Run `python3 run.py`, then load the relevant source table into an approved warehouse:

`outputs/daily_marketing.csv` → `analytics.daily_marketing`

Preserve numeric field types and parse dates as Date. Add these files to a Looker project, set `marketing_warehouse` to your actual connection, and update table qualification to your warehouse/dataset. Run LookML validation in Development Mode. Reconcile totals and filtered results with the CSV, including zero denominators. Promote only after checking permissions and dialect compatibility.

Do not join this independent study with unrelated project data. Aggregate ratios use sum numerators / sum denominators. Arm conversion rates are descriptive; formal experiment lift and uncertainty come from the Python estimator, not an average of displayed rates.

Looker and Looker Studio differ; these files target Looker. Reference: https://docs.cloud.google.com/looker/docs/reference/param-measure-types
