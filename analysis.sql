-- Latest ingestion wins on event identity. Aggregate each fact before joining.
-- A direct event-to-spend join would multiply spend by the number of members.
CREATE VIEW valid_members AS
WITH ranked AS (
 SELECT *, ROW_NUMBER() OVER (PARTITION BY member_id ORDER BY ingested_at DESC, ingestion_id DESC) AS rn
 FROM raw_members
)
SELECT member_id,date,campaign_id,net_revenue_usd FROM ranked
WHERE rn=1 AND net_revenue_usd>=0;

CREATE VIEW daily_marketing AS
WITH members AS (
 SELECT date,campaign_id,COUNT(*) AS new_members,SUM(net_revenue_usd) AS net_revenue_usd
 FROM valid_members GROUP BY 1,2
)
SELECT s.date,s.campaign_id,c.channel,s.spend_usd,
 COALESCE(m.new_members,0) AS new_members,COALESCE(m.net_revenue_usd,0) AS net_revenue_usd
FROM spend_daily s JOIN campaigns c ON s.campaign_id=c.campaign_id
LEFT JOIN members m ON s.date=m.date AND s.campaign_id=m.campaign_id;

CREATE VIEW weekly_marketing AS
SELECT strftime('%Y-%W',date) AS week,channel,SUM(spend_usd) AS spend_usd,
 SUM(new_members) AS new_members,SUM(net_revenue_usd) AS net_revenue_usd,
 SUM(spend_usd)/NULLIF(SUM(new_members),0) AS cac_usd
FROM daily_marketing GROUP BY 1,2;
