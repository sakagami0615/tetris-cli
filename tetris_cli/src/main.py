import tetris_cli.setting  # アプリケーション初期化（colorama等）
from tetris_cli.src.game import GameManager


def main():
    game_manager = GameManager()
    game_manager.game_loop()
    