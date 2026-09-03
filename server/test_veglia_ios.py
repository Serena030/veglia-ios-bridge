import tempfile
import unittest
from pathlib import Path

import veglia_ios


class StoreTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = veglia_ios.Store(Path(self.temp.name) / "state.json")

    def tearDown(self):
        self.temp.cleanup()

    def test_claims_one_watch_per_session(self):
        self.store.record("Game", "open", now=1000)
        self.assertIsNone(self.store.claim_due(15, now=1899))
        claim = self.store.claim_due(15, now=1900)
        self.assertEqual(claim["app"], "Game")
        self.assertEqual(claim["minutes"], 15)
        self.assertIsNone(self.store.claim_due(15, now=2000))

    def test_duplicate_open_does_not_reset_timer(self):
        self.store.record("Video", "open", now=1000)
        self.store.record("Video", "open", now=1500)
        self.assertEqual(self.store.status(now=1600)["current"]["seconds"], 600)

    def test_close_ends_session(self):
        self.store.record("Social", "open", now=1000)
        self.store.record("Social", "close", now=1100)
        self.assertIsNone(self.store.status(now=1200)["current"])
        self.assertIsNone(self.store.claim_due(1, now=1200))


if __name__ == "__main__":
    unittest.main()


