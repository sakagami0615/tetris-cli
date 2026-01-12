import copy

from tetris_cli.src.common.key import KeyManager, KeyState
from tetris_cli.src.common.trigger import TimeTrigger

from tetris_cli.src.tetris.board import Board
from tetris_cli.src.tetris.tetrimino import ActiveTetrimino
from tetris_cli.src.tetris.ui import Render
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
    active_mino: ActiveTetrimino | None
    hold_mino: ActiveTetrimino | None
    can_hold: bool

    def __init__(self):
        self.render = Render()
        self.board = Board()
        self.active_mino = ActiveTetrimino()
        self.hold_mino = None
        self.can_hold = True
        self.down_mino_trigger = TimeTrigger(interval=TETRIMINO_DROP_INTERVAL)

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

    def _is_valid_position(self, mino: ActiveTetrimino) -> bool:
        """テトリミノが有効な位置にあるかチェック"""
        for r, c in mino.blocks():
            cell = self.board.cells[r][c]
            if cell.fill:
                return False
        return True

    def _spawn_tetrimino(self) -> None:
        """新しいテトリミノをスポーン"""
        self.active_mino.spawn()

        # 新しいテトリミノでホールド可能にする
        self.can_hold = True

        if not self._is_valid_position(self.active_mino):
            self.active_mino = None
            self.is_continue = False

    def _apply_command(self, command: BasicCommand) -> bool:
        """基本コマンドを1つ適用し、成功したかどうかを返す"""
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

    def _create_ghost_mino(self) -> ActiveTetrimino | None:
        """ゴースト（落下予測位置）のテトリミノを作成"""
        if not self.active_mino:
            return None

        # アクティブミノの深いコピーを作成
        ghost_mino = copy.deepcopy(self.active_mino)

        # 着地するまで下に移動
        while True:
            ghost_mino.r += 1

            # 衝突チェック（一時的にactive_minoを置き換えて判定）
            original_r = self.active_mino.r
            self.active_mino.r = ghost_mino.r

            if not self._is_valid_position(self.active_mino):
                # 衝突したら1マス戻す
                ghost_mino.r -= 1
                self.active_mino.r = original_r
                break

            self.active_mino.r = original_r

        return ghost_mino

    def _execute_hard_drop(self) -> None:
        """ハードドロップを実行（着地するまで一気に落下）"""
        while True:
            # 1マス下に移動を試みる
            self.active_mino.r += 1

            # 衝突チェック
            if not self._is_valid_position(self.active_mino):
                # 衝突したら1マス戻して固定
                self.active_mino.r -= 1
                self.board.write_tetrimino(self.active_mino)
                self.board.clear_fill_lines()
                self._spawn_tetrimino()
                break

    def _execute_hold(self) -> None:
        """ホールドを実行（アクティブなテトリミノとホールドしているテトリミノを入れ替え）"""
        # ホールド可能かチェック
        if not self.can_hold:
            return

        if self.hold_mino is None:
            # 初回ホールド：アクティブなミノをホールドし、新しいミノをスポーン
            self.hold_mino = copy.deepcopy(self.active_mino)
            # 新しいミノをスポーン（_spawn_tetrimino を使わずに直接処理）
            self.active_mino.spawn()
            if not self._is_valid_position(self.active_mino):
                self.active_mino = None
                self.is_continue = False
        else:
            # 2回目以降：アクティブなミノとホールドしているミノを入れ替え
            temp = copy.deepcopy(self.active_mino)
            self.active_mino = copy.deepcopy(self.hold_mino)
            self.hold_mino = temp

            # 入れ替えたアクティブミノを初期位置に移動
            self.active_mino.spawn()
        
        # ホールドフラグを False にする
        self.can_hold = False

    def _apply_commands(self, commands: list[Command]) -> None:
        """コマンドを適用する"""
        if not commands:
            return

        # 特殊コマンドと基本コマンドを分離
        special_commands: list[SpecialCommand] = []
        basic_commands: list[BasicCommand] = []

        for command in commands:
            if isinstance(command, SpecialCommand):
                special_commands.append(command)
            elif isinstance(command, BasicCommand):
                basic_commands.append(command)

        # 特殊コマンドがある場合は他のコマンドを無視して即座に実行
        if special_commands:
            for special_command in special_commands:
                if isinstance(special_command, MoveHardDropCommand):
                    self._execute_hard_drop()
                elif isinstance(special_command, HoldCommand):
                    self._execute_hold()
            return

        # 基本コマンドを処理（下移動コマンドとそれ以外を分離）
        down_command: MoveDownCommand | None = None
        other_commands: list[BasicCommand] = []

        for command in basic_commands:
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
        # ゴーストミノを作成
        ghost_mino = self._create_ghost_mino()
        self.render.draw(self.board, self.active_mino, ghost_mino, self.hold_mino, is_cursor_up)
