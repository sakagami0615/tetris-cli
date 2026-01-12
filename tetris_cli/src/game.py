from tetris_cli.src.board import Board
from tetris_cli.src.key import KeyManager, KeyState
from tetris_cli.src.trigger import TimeTrigger
from tetris_cli.src.tetrimino import ActiveTetrimino
from tetris_cli.src.ui import Render
from tetris_cli.src.command import (
    Command, RotateCommand, MoveLeftCommand,
    MoveRightCommand, MoveDownCommand
)
from tetris_cli.src.const import (
    HOT_KEY_QUIT, HOT_KEY_MINO_ROTATE_CW, HOT_KEY_MINO_MOVE_DOWN,
    HOT_KEY_MINO_MOVE_RIGHT, HOT_KEY_MINO_MOVE_LEFT, GAME_LOOP_TRIGGER_TIME,
    TETRIMINO_DROP_INTERVAL, TETRIMINO_SPAWN_ROW, TETRIMINO_SPAWN_COL,
    KEY_REPEAT_INTERVAL
)
from tetris_cli.src import console


class Game:
    """ゲームのメインロジックを管理"""
    is_continue: bool = True
    down_mino_trigger: TimeTrigger
    render: Render
    board: Board
    active_mino: ActiveTetrimino | None

    def __init__(self):
        self.render = Render()
        self.board = Board()
        self.active_mino = ActiveTetrimino(TETRIMINO_SPAWN_ROW, TETRIMINO_SPAWN_COL)
        self.down_mino_trigger = TimeTrigger(interval=TETRIMINO_DROP_INTERVAL)

    def _get_input_commands(self) -> list[Command]:
        """キー入力から実行すべきコマンドのリストを取得"""
        commands: list[Command] = []
        key_manager = KeyManager()

        # 回転
        key_rot_cw = key_manager.get_key_input(HOT_KEY_MINO_ROTATE_CW)
        if key_rot_cw.state == KeyState.PRESS and key_rot_cw.elapsed % KEY_REPEAT_INTERVAL == 0:
            commands.append(RotateCommand())

        # 左移動
        key_move_left = key_manager.get_key_input(HOT_KEY_MINO_MOVE_LEFT)
        if key_move_left.state == KeyState.PRESS and key_move_left.elapsed % KEY_REPEAT_INTERVAL == 0:
            commands.append(MoveLeftCommand())

        # 右移動
        key_move_right = key_manager.get_key_input(HOT_KEY_MINO_MOVE_RIGHT)
        if key_move_right.state == KeyState.PRESS and key_move_right.elapsed % KEY_REPEAT_INTERVAL == 0:
            commands.append(MoveRightCommand())

        # 下移動（自動 or キー入力）
        key_move_down = key_manager.get_key_input(HOT_KEY_MINO_MOVE_DOWN)
        if (self.down_mino_trigger.is_trigger() or
            (key_move_down.state == KeyState.PRESS and key_move_down.elapsed % KEY_REPEAT_INTERVAL == 0)):
            commands.append(MoveDownCommand())

        return commands

    def _is_valid_position(self, mino: ActiveTetrimino) -> bool:
        """テトリミノが有効な位置にあるかチェック"""
        for r, c in mino.blocks():
            cell = self.board.cells[r][c]
            if cell.fill:
                return False
        return True

    def _spawn_tetrimino(self) -> None:
        """新しいテトリミノをスポーン"""
        self.active_mino.spawn(TETRIMINO_SPAWN_ROW, TETRIMINO_SPAWN_COL)
        if not self._is_valid_position(self.active_mino):
            self.active_mino = None
            self.is_continue = False

    def _apply_command(self, command: Command) -> bool:
        """コマンドを1つ適用し、成功したかどうかを返す"""
        # 現在の状態を保存
        original_r = self.active_mino.r
        original_c = self.active_mino.c
        original_rotate = self.active_mino.rotate

        # コマンドを実行
        move = command.execute()
        self.active_mino.r += move.dr
        self.active_mino.c += move.dc
        self.active_mino.rotate = (self.active_mino.rotate + move.d_rotate) % self.active_mino.n_rotate

        # 衝突チェック
        if not self._is_valid_position(self.active_mino):
            # 元の位置に戻す
            self.active_mino.r = original_r
            self.active_mino.c = original_c
            self.active_mino.rotate = original_rotate
            return False

        return True

    def _apply_commands(self, commands: list[Command]) -> None:
        """コマンドを適用する"""
        if not commands:
            return

        # 下移動コマンドとそれ以外を分離
        down_command = None
        other_commands = []

        for command in commands:
            if isinstance(command, MoveDownCommand):
                down_command = command
            else:
                other_commands.append(command)

        # 回転・左右移動を先に処理
        for command in other_commands:
            self._apply_command(command)

        # 下移動を最後に処理
        if down_command:
            if not self._apply_command(down_command):
                # 下移動で衝突した場合は固定
                self.board.write_tetrimino(self.active_mino)
                self.board.clear_fill_lines()
                self._spawn_tetrimino()

    def update(self) -> None:
        """ゲーム状態を更新"""
        commands = self._get_input_commands()
        self._apply_commands(commands)

    def draw(self, is_cursor_up: bool = True):
        """画面を描画する"""
        self.render.draw(self.board, self.active_mino, is_cursor_up)


class GameManager:
    """ゲーム全体を管理するマネージャークラス"""
    game: Game
    game_loop_trigger: TimeTrigger

    def __init__(self):
        self.game = Game()
        self.game_loop_trigger = TimeTrigger(interval=GAME_LOOP_TRIGGER_TIME)

    def __del__(self):
        self.game.draw(is_cursor_up=False)

    def _is_quit(self) -> bool:
        """終了キーが押されたかチェック"""
        quit_key = KeyManager().get_key_input(HOT_KEY_QUIT)
        return quit_key.state == KeyState.PRESS

    def game_loop(self) -> None:
        """ゲームループを実行"""
        try:
            while self.game.is_continue:
                if self.game_loop_trigger.is_trigger():
                    self.game.update()
                    self.game.draw()
                    KeyManager().update()

                if self._is_quit():
                    break
        finally:
            KeyManager().stop()
            console.clear_input_buffer()
