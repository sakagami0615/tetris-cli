from tetris_cli.src.common import console
from tetris_cli.src.common.key import KeyManager, KeyState
from tetris_cli.src.common.trigger import TimeTrigger

from tetris_cli.src.tetris.game import Game
from tetris_cli.src.tetris.const import (
    HOT_KEY_QUIT, GAME_LOOP_TRIGGER_TIME, HOT_KEY_LIST
)


class GameManager:
    """ゲーム全体を管理するマネージャークラス"""
    _game: Game
    _game_loop_trigger: TimeTrigger
    _old_terminal_settings = None

    def __init__(self):
        self._game = Game()
        self._game_loop_trigger = TimeTrigger(interval=GAME_LOOP_TRIGGER_TIME)
        # ターミナルのエコーを無効化（キー入力を画面に表示しない）
        self._old_terminal_settings = console.disable_echo()

    def __del__(self):
        # 最終描画
        self._game.draw(is_cursor_up=False)
        # ターミナル設定を元に戻す
        console.restore_echo(self._old_terminal_settings)

    def _is_quit(self) -> bool:
        """終了キーが押されたかチェック"""
        quit_key = KeyManager(HOT_KEY_LIST).get_key_input(HOT_KEY_QUIT)
        return quit_key.state == KeyState.PRESS

    def game_loop(self) -> None:
        """ゲームループを実行"""
        try:
            while self._game.is_continue:
                if self._game_loop_trigger.is_trigger():
                    self._game.update()
                    self._game.draw()
                    KeyManager(HOT_KEY_LIST).update()

                if self._is_quit():
                    break
        finally:
            KeyManager(HOT_KEY_LIST).stop()
            console.clear_input_buffer()
            # ターミナル設定を元に戻す
            console.restore_echo(self._old_terminal_settings)


def run():
    game_manager = GameManager()
    game_manager.game_loop()
    