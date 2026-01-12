import unittest
from tetris_cli.src.tetris.score import ScoreManager

class TestScoreManager(unittest.TestCase):
    def setUp(self):
        self.score_manager = ScoreManager()

    def test_initial_score(self):
        """初期スコアが0であることを確認"""
        self.assertEqual(self.score_manager.score, 0)

    def test_add_score(self):
        """ライン数に応じたスコア加算を確認"""
        # 1ライン消去: +100
        self.score_manager.add_score(1)
        self.assertEqual(self.score_manager.score, 100)
        
        # 2ライン消去: +300
        self.score_manager.add_score(2)
        self.assertEqual(self.score_manager.score, 100 + 300)
        
        # 3ライン消去: +500
        self.score_manager.add_score(3)
        self.assertEqual(self.score_manager.score, 400 + 500)
        
        # 4ライン消去: +800
        self.score_manager.add_score(4)
        self.assertEqual(self.score_manager.score, 900 + 800)