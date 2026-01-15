from tetris_cli.src.common.key import KeyManager, KeyState
from tetris_cli.src.common.trigger import TimeTrigger

from tetris_cli.src.tetris.board import Board
from tetris_cli.src.tetris.tetrimino import Tetrimino, TetriminoManager
from tetris_cli.src.tetris.ui import Render
from tetris_cli.src.tetris.score import ScoreManager
from tetris_cli.src.tetris.command import (
    Command, BasicCommand, SpecialCommand,
    RotateCwCommand, RotateCcwCommand, MoveLeftCommand,
    MoveRightCommand, MoveDownCommand, MoveHardDropCommand, HoldCommand
)
from tetris_cli.src.tetris.const import (
    HOT_KEY_MINO_ROTATE_CW, HOT_KEY_MINO_ROTATE_CCW, HOT_KEY_MINO_MOVE_DOWN,
    HOT_KEY_MINO_MOVE_RIGHT, HOT_KEY_MINO_MOVE_LEFT, HOT_KEY_MINO_MOVE_HARD_DROP, HOT_KEY_MINO_HOLD,
    TETRIMINO_DROP_INTERVAL, KEY_REPEAT_INTERVAL, HOT_KEY_LIST
)

class Game:
    """ゲームのメインロジックを管理"""
    is_continue: bool = True
    down_mino_trigger: TimeTrigger
    render: Render
    board: Board
    tetrimino_manager: TetriminoManager
    score_manager: ScoreManager

    def __init__(self):
        self.render = Render()
        self.board = Board()
        self.tetrimino_manager = TetriminoManager()
        self.down_mino_trigger = TimeTrigger(interval=TETRIMINO_DROP_INTERVAL)
        self.score_manager = ScoreManager()

    @property
    def score(self) -> int:
        return self.score_manager.score

    def _get_input_commands(self) -> list[Command]:
        """キー入力から実行すべきコマンドのリストを取得"""
        commands: list[Command] = []
        key_manager = KeyManager(HOT_KEY_LIST)

        # 時計回り回転
        key_rot_cw = key_manager.get_key_input(HOT_KEY_MINO_ROTATE_CW)
        if key_rot_cw.state == KeyState.PRESS and key_rot_cw.elapsed % KEY_REPEAT_INTERVAL == 0:
            commands.append(RotateCwCommand())

        # 反時計回り回転
        key_rot_ccw = key_manager.get_key_input(HOT_KEY_MINO_ROTATE_CCW)
        if key_rot_ccw.state == KeyState.PRESS and key_rot_ccw.elapsed % KEY_REPEAT_INTERVAL == 0:
            commands.append(RotateCcwCommand())

        # 左移動
        key_move_left = key_manager.get_key_input(HOT_KEY_MINO_MOVE_LEFT)
        if key_move_left.state == KeyState.PRESS and key_move_left.elapsed % KEY_REPEAT_INTERVAL == 0:
            commands.append(MoveLeftCommand())

        # 右移動
        key_move_right = key_manager.get_key_input(HOT_KEY_MINO_MOVE_RIGHT)
        if key_move_right.state == KeyState.PRESS and key_move_right.elapsed % KEY_REPEAT_INTERVAL == 0:
            commands.append(MoveRightCommand())

        # ハードドロップ
        key_hard_drop = key_manager.get_key_input(HOT_KEY_MINO_MOVE_HARD_DROP)
        if key_hard_drop.state == KeyState.PRESS and key_hard_drop.elapsed % KEY_REPEAT_INTERVAL == 0:
            commands.append(MoveHardDropCommand())

        # ホールド
        key_hold = key_manager.get_key_input(HOT_KEY_MINO_HOLD)
        if key_hold.state == KeyState.PRESS and key_hold.elapsed % KEY_REPEAT_INTERVAL == 0:
            commands.append(HoldCommand())

        # 下移動（自動 or キー入力）
        key_move_down = key_manager.get_key_input(HOT_KEY_MINO_MOVE_DOWN)
        if (self.down_mino_trigger.is_trigger() or
            (key_move_down.state == KeyState.PRESS and key_move_down.elapsed % KEY_REPEAT_INTERVAL == 0)):
            commands.append(MoveDownCommand())

        return commands

    def _is_valid_position(self, mino: Tetrimino) -> bool:
        """テトリミノが有効な位置にあるかチェック"""
        for r, c in mino.blocks():
            cell = self.board.cells[r][c]
            if cell.fill:
                return False
        return True

    def _spawn_tetrimino(self) -> None:
        """新しいテトリミノをスポーン"""
        if not self.tetrimino_manager.spawn(self._is_valid_position):
            # スポーンできなかった場合はゲームオーバー
            self.is_continue = False

    def _create_ghost_mino(self) -> Tetrimino | None:
        """ゴースト（落下予測位置）のテトリミノを作成"""
        return self.tetrimino_manager.create_ghost(self._is_valid_position)

    def _execute_hard_drop(self) -> None:
        """ハードドロップを実行（着地するまで一気に落下）"""
        active_mino = self.tetrimino_manager.active_mino

        while True:
            # 1マス下に移動を試みる
            active_mino.r += 1

            # 衝突チェック
            if not self._is_valid_position(active_mino):
                # 衝突したら1マス戻して固定
                active_mino.r -= 1
                self.board.write_tetrimino(active_mino)
                cleared_lines = self.board.clear_fill_lines()
                self.score_manager.add_score(cleared_lines)
                self._spawn_tetrimino()
                break

    def _execute_hold(self) -> None:
        """ホールドを実行（アクティブなテトリミノとホールドしているテトリミノを入れ替え）"""
        if not self.tetrimino_manager.hold(self._is_valid_position):
            # ホールドきなかった場合はゲームオーバー
            self.is_continue = False

    def _apply_special_command(self, command: SpecialCommand) -> bool:
        """特殊コマンドを1つ適用し、実施したかどうかを返す"""
        if isinstance(command, MoveHardDropCommand):
            self._execute_hard_drop()
            return True
        elif isinstance(command, HoldCommand):
            self._execute_hold()
            return True
        return False

    def _apply_basic_command(self, command: BasicCommand) -> bool:
        """基本コマンドを1つ適用し、成功したかどうかを返す"""
        active_mino = self.tetrimino_manager.active_mino

        # 現在の状態を保存
        original_r = active_mino.r
        original_c = active_mino.c
        original_rotate = active_mino.rotate

        # コマンドを実行
        move = command.execute()
        active_mino.r += move.dr
        active_mino.c += move.dc
        active_mino.rotate = (active_mino.rotate + move.d_rotate) % active_mino.n_rotate

        # 衝突チェック
        if not self._is_valid_position(active_mino):
            # 元の位置に戻す
            active_mino.r = original_r
            active_mino.c = original_c
            active_mino.rotate = original_rotate
            return False

        return True

    def _apply_commands(self, commands: list[Command]) -> None:
        """コマンドを適用する"""
        if not commands:
            return

        def split_commands(commands):
            """特殊コマンドと基本コマンドを分離"""
            special_commands = [command for command in commands if isinstance(command, SpecialCommand)]
            basic_commands = [command for command in commands if isinstance(command, BasicCommand)]
            
            control_commands: list[MoveDownCommand] = []
            down_command: MoveDownCommand | None = None
            for basic_command in basic_commands:
                if isinstance(basic_command, MoveDownCommand):
                    down_command = basic_command
                else:
                    control_commands.append(basic_command)

            return special_commands, control_commands, down_command

        special_commands, control_commands, down_command = split_commands(commands)

        # 特殊コマンドがある場合は他のコマンドを無視して即座に実行
        for special_command in special_commands:
            if self._apply_special_command(special_command):
                return

        # 回転・左右移動を先に処理
        for command in control_commands:
            self._apply_basic_command(command)

        # 下移動を最後に処理
        if down_command:
            if not self._apply_basic_command(down_command):
                # 下移動で衝突した場合は固定
                active_mino = self.tetrimino_manager.active_mino
                self.board.write_tetrimino(active_mino)
                cleared_lines = self.board.clear_fill_lines()
                self.score_manager.add_score(cleared_lines)
                self._spawn_tetrimino()

    def update(self) -> None:
        """ゲーム状態を更新"""
        commands = self._get_input_commands()
        self._apply_commands(commands)

    def draw(self, is_cursor_up: bool = True):
        """画面を描画する"""
        # ゴーストミノを作成
        ghost_mino = self._create_ghost_mino()
        active_mino = self.tetrimino_manager.active_mino
        hold_mino = self.tetrimino_manager.hold_mino
        next_minos = self.tetrimino_manager.next_minos
        self.render.draw(self.board, active_mino, ghost_mino, hold_mino, next_minos, self.score, is_cursor_up)
