from tetris_cli.src.common import console
from tetris_cli.src.common.key import KeyManager, KeyState
from tetris_cli.src.common.trigger import TimeTrigger

from tetris_cli.src.tetris.game import Game
from tetris_cli.src.tetris.const import (
    HOT_KEY_QUIT, GAME_LOOP_TRIGGER_TIME, HOT_KEY_LIST
)


class GameManager:
    """ゲーム全体を管理するマネージャークラス"""
    game: Game
    game_loop_trigger: TimeTrigger

    def __init__(self):
        self.game = Game()
        self.game_loop_trigger = TimeTrigger(interval=GAME_LOOP_TRIGGER_TIME)

    def __del__(self):
        # 最終描画（ゴーストミノも作成）
        ghost_mino = self.game._create_ghost_mino()
        self.game.render.draw(self.game.board, self.game.active_mino, ghost_mino, self.game.hold_mino, self.game.score, is_cursor_up=False)

    def _is_quit(self) -> bool:
        """終了キーが押されたかチェック"""
        quit_key = KeyManager(HOT_KEY_LIST).get_key_input(HOT_KEY_QUIT)
        return quit_key.state == KeyState.PRESS

    def game_loop(self) -> None:
        """ゲームループを実行"""
        try:
            while self.game.is_continue:
                if self.game_loop_trigger.is_trigger():
                    self.game.update()
                    self.game.draw()
                    KeyManager(HOT_KEY_LIST).update()

                if self._is_quit():
                    break
        finally:
            KeyManager(HOT_KEY_LIST).stop()
            console.clear_input_buffer()
