import tetris_cli.setting  # 設定処理実施
from tetris_cli.src.game_manager import GameManager


def main():
    game_manager = GameManager()
    game_manager.game_loop()
    