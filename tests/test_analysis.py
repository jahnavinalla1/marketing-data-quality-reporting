import math
import sqlite3
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import run
lift=budget=reporting=run

class PipelineTests(unittest.TestCase):
    def connect(self,project):
        source=sqlite3.connect(ROOT/'outputs/analysis.sqlite')
        db=sqlite3.connect(':memory:');source.backup(db);source.close()
        db.row_factory=sqlite3.Row
        self.addCleanup(db.close)
        return db

    def test_known_quarantine_and_clean_release(self):
        db=self.connect('04-trusted-marketing-reporting')
        checks={r['check_name']:r for r in reporting.checks(db)}
        self.assertEqual(checks['duplicate_ingestions']['observed'],12)
        self.assertEqual(checks['negative_revenue']['observed'],1)
        self.assertEqual(checks['unmatched_member_campaign']['observed'],1)
        self.assertFalse(any(r['status']=='FAIL' for r in checks.values()))

    def test_duplicate_spend_blocks_release(self):
        db=self.connect('04-trusted-marketing-reporting')
        db.execute('INSERT INTO spend_daily SELECT * FROM spend_daily LIMIT 1')
        checks={r['check_name']:r for r in reporting.checks(db)}
        self.assertEqual(checks['spend_key_uniqueness']['status'],'FAIL')

    def test_unknown_spend_blocks_release(self):
        db=self.connect('04-trusted-marketing-reporting')
        db.execute("INSERT INTO spend_daily VALUES ('2026-09-28','UNKNOWN',100)")
        checks={r['check_name']:r for r in reporting.checks(db)}
        self.assertEqual(checks['unknown_spend_campaign']['status'],'FAIL')

    def test_stale_data_blocks_release(self):
        db=self.connect('04-trusted-marketing-reporting')
        db.execute("DELETE FROM spend_daily WHERE date>'2026-09-20'")
        checks={r['check_name']:r for r in reporting.checks(db)}
        self.assertEqual(checks['freshness_days']['status'],'FAIL')

if __name__=='__main__':unittest.main()
