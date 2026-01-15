class ScoreManager:
    """スコア計算と管理を行うクラス"""
    _score: int

    def __init__(self):
        self._score = 0

    @property
    def score(self) -> int:
        """現在のスコアを取得"""
        return self._score

    def add_score(self, lines: int) -> None:
        """消去したライン数に基づいてスコアを加算"""
        if lines == 1:
            self._score += 100
        elif lines == 2:
            self._score += 300
        elif lines == 3:
            self._score += 500
        elif lines == 4:
            self._score += 800