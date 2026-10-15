import json
import sqlite3
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch
from daily_review import run_demo, summarize, run_cloud


class DailyReviewTests(unittest.TestCase):
    def test_deadlines_exclude_finished_and_future(self):
        items = [{"status": "draft", "due_date": "2026-10-14"},
                 {"status": "ready", "due_date": "2026-10-15"},
                 {"status": "idea", "due_date": "2026-10-16"},
                 {"status": "published", "due_date": "2026-10-14"},
                 {"status": "archived", "due_date": "2026-10-14"}]
        report = summarize(items, date(2026, 10, 15))
        self.assertEqual(report["due_items"], 2)
        self.assertEqual(report["total_items"], 5)

    def test_rerun_does_not_duplicate_day(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "demo.db"
            for day in [15, 15, 16]:
                run_demo(date(2026, 10, day), path)
            with sqlite3.connect(path) as db:
                self.assertEqual(db.execute("select count(*) from daily_reviews").fetchone()[0], 2)

    @patch.dict("os.environ", {"SUPABASE_URL": "https://example.supabase.co",
                              "SUPABASE_SECRET_KEY": "sb_secret_test"})
    @patch("daily_review.request_json")
    def test_pagination_and_upsert_contract(self, request):
        request.side_effect = [[{"status": "idea", "due_date": None}],
                               [{"status": "draft", "due_date": None}], [], None]
        result = run_cloud(date(2026, 10, 15))
        self.assertEqual(result["total_items"], 2)
        self.assertIn("offset=1", request.call_args_list[1].args[2])
        self.assertEqual(request.call_args.args[2], "daily_reviews?on_conflict=review_date,timezone")


if __name__ == "__main__":
    unittest.main()
