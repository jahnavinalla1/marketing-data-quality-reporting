- dashboard: trusted_marketing_portfolio
  title: "Trusted Marketing Data & Reporting — Synthetic Data"
  layout: newspaper
  preferred_viewer: dashboards-next
  elements:
  - name: primary_view
    title: "Trusted Marketing Data & Reporting"
    model: marketing
    explore: trusted_marketing
    type: looker_line
    fields: [trusted_marketing.activity_date, trusted_marketing.cac]
    row: 0
    col: 0
    width: 24
    height: 10
