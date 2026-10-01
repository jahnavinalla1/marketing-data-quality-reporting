"""SQL reporting pipeline with known defects, reconciliation, and a release gate."""
import random
import sys
from datetime import date,timedelta
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import database, query, report, table, write_csv

ROOT=Path(__file__).resolve().parent


def build(db): db.executescript((ROOT/'analysis.sql').read_text())


def checks(db):
    """Failures block release; warnings represent explicitly quarantined records."""
    specifications=[
        ('spend_key_uniqueness','blocker',"SELECT COUNT(*) AS n FROM (SELECT date,campaign_id FROM spend_daily GROUP BY 1,2 HAVING COUNT(*)>1)"),
        ('dimension_key_uniqueness','blocker',"SELECT COUNT(*) AS n FROM (SELECT campaign_id FROM campaigns GROUP BY 1 HAVING COUNT(*)>1)"),
        ('negative_spend','blocker','SELECT COUNT(*) AS n FROM spend_daily WHERE spend_usd<0'),
        ('unknown_spend_campaign','blocker','SELECT COUNT(*) AS n FROM spend_daily s LEFT JOIN campaigns c USING(campaign_id) WHERE c.campaign_id IS NULL'),
        ('unmatched_member_campaign','warning','SELECT COUNT(*) AS n FROM valid_members m LEFT JOIN campaigns c USING(campaign_id) WHERE c.campaign_id IS NULL'),
        ('negative_revenue','warning','SELECT COUNT(*) AS n FROM raw_members WHERE net_revenue_usd<0'),
        ('duplicate_ingestions','warning','SELECT COUNT(*)-COUNT(DISTINCT member_id) AS n FROM raw_members'),
        ('missing_member_spend_key','warning','SELECT COUNT(*) AS n FROM valid_members m LEFT JOIN spend_daily s ON m.date=s.date AND m.campaign_id=s.campaign_id WHERE s.campaign_id IS NULL'),
        ('spend_reconciliation','blocker','SELECT ABS((SELECT SUM(spend_usd) FROM spend_daily)-(SELECT SUM(spend_usd) FROM daily_marketing)) AS n'),
        ('member_reconciliation','blocker','SELECT ABS((SELECT COUNT(*) FROM valid_members m WHERE EXISTS (SELECT 1 FROM spend_daily s WHERE s.date=m.date AND s.campaign_id=m.campaign_id))-(SELECT SUM(new_members) FROM daily_marketing)) AS n'),
        ('freshness_days','blocker',"SELECT julianday('2026-09-29')-julianday(MAX(date)) AS n FROM spend_daily"),
    ]
    result=[]
    for name,severity,sql in specifications:
        observed=query(db,sql)[0]['n']
        threshold=1 if name=='freshness_days' else .000001
        ok=observed is not None and abs(observed)<=threshold
        result.append(dict(check_name=name,severity=severity,observed=observed,status='PASS' if ok else 'WARN' if severity=='warning' else 'FAIL'))
    return result


def main():
    rng=random.Random(74)
    campaigns=[dict(campaign_id=f'C{i}',channel=c) for i,c in enumerate(['Search','Social','Display','Affiliate'])]
    spend=[]; events=[]
    for d in range(28):
        day=str(date(2026,9,1)+timedelta(days=d))
        for c in campaigns:
            spend.append(dict(date=day,campaign_id=c['campaign_id'],spend_usd=round(rng.uniform(250,700),2)))
            for _ in range(rng.randint(8,22)):
                i=len(events)
                events.append(dict(ingestion_id=i,member_id=f'M{i}',date=day,campaign_id=c['campaign_id'],net_revenue_usd=136.8,ingested_at=day+'T12:00:00'))
    # Intentionally inject replayed ingestions, one invalid value, and one unmapped campaign.
    for original in events[:12]:
        events.append(dict(original,ingestion_id=len(events),ingested_at='2026-09-29T01:00:00'))
    events.append(dict(ingestion_id=len(events),member_id='bad-value',date='2026-09-20',campaign_id='C0',net_revenue_usd=-10.0,ingested_at='2026-09-20T12:00:00'))
    events.append(dict(ingestion_id=len(events),member_id='unmapped',date='2026-09-20',campaign_id='UNKNOWN',net_revenue_usd=136.8,ingested_at='2026-09-20T12:00:00'))
    for name,rows in [('spend_daily',spend),('raw_members',events),('campaigns',campaigns)]:write_csv(ROOT/f'data/{name}.csv',rows)
    db=database(ROOT/'outputs/analysis.sqlite',{'spend_daily':spend,'raw_members':events,'campaigns':campaigns})
    build(db)
    quality=checks(db)
    if any(r['status']=='FAIL' for r in quality):raise RuntimeError('Blocking data-quality check failed')
    daily=query(db,'SELECT * FROM daily_marketing ORDER BY date,campaign_id')
    weekly=query(db,'SELECT * FROM weekly_marketing ORDER BY week,channel')
    quarantined=query(db,"SELECT member_id, 'negative_revenue' AS reason FROM raw_members WHERE net_revenue_usd<0 UNION ALL SELECT member_id,'missing_spend_key' AS reason FROM valid_members m WHERE NOT EXISTS (SELECT 1 FROM spend_daily s WHERE s.date=m.date AND s.campaign_id=m.campaign_id)")
    for name,rows in [('daily_marketing',daily),('weekly_marketing',weekly),('quality_checks',quality),('quarantine',quarantined)]:write_csv(ROOT/f'outputs/{name}.csv',rows)
    inflation=query(db,'SELECT SUM(s.spend_usd)/(SELECT SUM(spend_usd) FROM spend_daily) AS factor FROM spend_daily s JOIN raw_members m ON s.date=m.date AND s.campaign_id=m.campaign_id')[0]['factor']
    report(ROOT,'Trusted Marketing Data & Weekly Reporting',{'Duplicate replays':12,'Quarantined members':len(quarantined),'Blocking failures':0,'Naive join inflation':f'{inflation:.1f}×'},
           [table('Weekly acquisition report',weekly,'channel','cac_usd'),table('Data quality checks',quality,'check_name','observed'),table('Daily reporting mart',daily,'date','spend_usd')],
           [f"Joining raw member events directly to daily spend would inflate spend by {inflation:.1f}×. Aggregate facts to date/campaign grain before joining.",
            'Deduplicate 12 replayed ingestions, exclude one invalid revenue record, and quarantine one unmapped acquisition. Report warnings visibly rather than silently losing records.',
            'The clean mart reconciles to source spend and eligible distinct members. Release with disclosed warnings; route unmapped campaigns to Marketing Operations and invalid amounts to the source owner.',
            'Freshness is evaluated against the fixed simulation as-of date 2026-09-29. The recurring run must use a production as-of parameter and an agreed ingestion SLA.'],
           'Synthetic ingestion exercise. One row per member represents one acquisition; this is not a full order ledger. Raw inputs deliberately include known defects. WARN checks overlap and must not be summed as distinct incidents. Nonnegative net receipts are required by this acquisition contract; refund transactions need a separate ledger. Media spend is USD and timestamps are UTC. The final week is partial, so do not compare unadjusted weekly totals. No live platform connector or scheduled production job is deployed.')
    db.close()


if __name__=='__main__':main()
