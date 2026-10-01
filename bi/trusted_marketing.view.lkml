view: trusted_marketing {
  sql_table_name: analytics.daily_marketing ;;
  dimension: channel { type: string sql: ${TABLE}.channel ;; }
  dimension: campaign_id { type: string sql: ${TABLE}.campaign_id ;; }
  dimension_group: activity { type: time timeframes: [date, week, month] sql: ${TABLE}.date ;; }
  measure: spend { type: sum sql: ${TABLE}.spend_usd ;; value_format_name: usd }
  measure: members { type: sum sql: ${TABLE}.new_members ;; }
  measure: net_revenue { type: sum sql: ${TABLE}.net_revenue_usd ;; value_format_name: usd }
  measure: cac { type: number sql: 1.0 * ${spend} / NULLIF(${members},0) ;; value_format_name: usd }
}
