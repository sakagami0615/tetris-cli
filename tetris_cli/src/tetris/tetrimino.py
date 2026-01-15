import copy
import random
from enum import Enum
from dataclasses import dataclass

from tetris_cli.src.common.color import Color
from tetris_cli.src.tetris.const import TETRIMINO_SPAWN_ROW, TETRIMINO_SPAWN_COL


TETRIMINO_COLORS = [
    Color.YELLOW.value,
    Color.SKYBLUE.value,
    Color.ORANGE.value,
    Color.BLUE.value,
    Color.GREEN.value,
    Color.RED.value,
    Color.PINK.value,
]

N_TETRIMINO = len(TETRIMINO_COLORS)

MINO_O_INDEX = 0
MINO_I_INDEX = 1
MINO_L_INDEX = 2
MINO_J_INDEX = 3
MINO_S_INDEX = 4
MINO_Z_INDEX = 5
MINO_T_INDEX = 6


@dataclass(frozen=True)
class TetriminoDefine:
    rotations: list[list[tuple[int, int]]]
    color: tuple[int, int, int]


class TetriminoType(Enum):
    """
    ■ ■ 
    □ ■ 
    """
    MINO_O = TetriminoDefine(
        rotations = [
            [( 0,  0), (-1,  0), (-1,  1), ( 0,  1)],
        ],
        color = TETRIMINO_COLORS[MINO_O_INDEX],
    )
    """
    ■ □ ■ ■
    """
    MINO_I = TetriminoDefine(
        rotations = [
            [( 0,  0), ( 0, -1), ( 0,  1), ( 0,  2)],
            [( 0,  0), (-1,  0), ( 1,  0), ( 2,  0)],
        ],
        color = TETRIMINO_COLORS[MINO_I_INDEX],
    )
    """
        ■
    ■ □ ■
    """
    MINO_L = TetriminoDefine(
        rotations = [
            [( 0,  0), (-1, -1), ( 0, -1), ( 0,  1)],
            [( 0,  0), (-1,  0), ( 1,  0), (-1,  1)],
            [( 0,  0), ( 0, -1), ( 0,  1), ( 1,  1)],
            [( 0,  0), (-1,  0), ( 1,  0), ( 1, -1)],
        ],
        color = TETRIMINO_COLORS[MINO_L_INDEX],
    )
    """
    ■
    ■ □ ■
    """
    MINO_J = TetriminoDefine(
        rotations = [
            [( 0,  0), (-1,  1), ( 0, -1), ( 0,  1)],
            [( 0,  0), (-1,  0), ( 1,  0), ( 1,  1)],
            [( 0,  0), ( 0, -1), ( 0,  1), ( 1, -1)],
            [( 0,  0), (-1,  0), (-1, -1), ( 1,  0)],
        ],
        color = TETRIMINO_COLORS[MINO_J_INDEX],
    )
    """
      ■ ■
    ■ □
    """
    MINO_S = TetriminoDefine(
        rotations = [
            [( 0,  0), ( 0, -1), (-1,  0), (-1,  1)],
            [( 0,  0), (-1,  0), ( 0,  1), ( 1,  1)],
        ],
        color = TETRIMINO_COLORS[MINO_S_INDEX],
    )
    """
    ■ ■
      □ ■
    """
    MINO_Z = TetriminoDefine(
        rotations = [
            [( 0,  0), ( 0,  1), (-1,  0), (-1, -1)],
            [( 0,  0), ( 1,  0), ( 0,  1), (-1,  1)],
        ],
        color = TETRIMINO_COLORS[MINO_Z_INDEX],
    )
    """
      ■
    ■ □ ■
    """
    MINO_T = TetriminoDefine(
        rotations = [
            [( 0,  0), (-1,  0), ( 0, -1), ( 0,  1)],
            [( 0,  0), (-1,  0), ( 0,  1), ( 1,  0)],
            [( 0,  0), ( 0, -1), ( 0,  1), ( 1,  0)],
            [( 0,  0), (-1,  0), ( 0, -1), ( 1,  0)],
        ],
        color = TETRIMINO_COLORS[MINO_T_INDEX],
    )


class TetriminoSpawner:
    """テトリミノのスポーン順序を管理するクラス

    7種類のテトリミノをランダムな順序で出現させる。
    全7種類が出現したら再度シャッフルして繰り返す（7-bag方式）。
    """
    _base_type_list: list[TetriminoDefine]
    _next_type_list: list[TetriminoDefine]

    _curr_index: int
    _n_type: int

    def __init__(self):
        self._base_type_list = [
            TetriminoType.MINO_O.value,
            TetriminoType.MINO_I.value,
            TetriminoType.MINO_L.value,
            TetriminoType.MINO_J.value,
            TetriminoType.MINO_S.value,
            TetriminoType.MINO_Z.value,
            TetriminoType.MINO_T.value,
        ]
        self._n_type = len(self._base_type_list)

        # NOTE: 次ミノを2回補充して十分な個数確保しておく
        self._next_type_list = []
        self._replenish_next_tetrimino()
        self._replenish_next_tetrimino()

    def _replenish_next_tetrimino(self):
        type_list = self._base_type_list[:]
        random.shuffle(type_list)
        self._next_type_list += type_list

    def get_next_tetrimino(self) -> TetriminoDefine:
        """次のテトリミノタイプを取得

        7種類全てが出現したら、リストをシャッフルして新しいサイクルを開始する。
        """
        # 次のミノをpopする
        next_mino = self._next_type_list.pop(0)

        # 次のテトリミノが少なくなったら補充する
        if len(self._next_type_list) < self._n_type:
            self._replenish_next_tetrimino()

        return next_mino

    def peek_next_tetrimino_list(self, count: int) -> list[TetriminoDefine]:
        """次に出現する複数のテトリミノタイプを取得（消費しない）

        Args:
            count: 取得するテトリミノの数

        Returns:
            次に出現予定のテトリミノタイプのリスト
        """
        return self._next_type_list[:count]


class Tetrimino:
    """現在アクティブなテトリミノ

    位置、回転状態、ミノタイプを保持する値オブジェクト。
    スポーン処理はTetriminoManagerが担当する。
    """
    _mino_type: TetriminoDefine
    _r: int
    _c: int
    _rotate: int
    _n_rotate: int

    @property
    def r(self) -> int: return self._r
    @property
    def c(self) -> int: return self._c
    @property
    def rotate(self) -> int: return self._rotate
    @property
    def n_rotate(self) -> int: return self._n_rotate
    @property
    def mino_type(self) -> TetriminoDefine: return self._mino_type
    @r.setter
    def r(self, v: int): self._r = v
    @c.setter
    def c(self, v: int): self._c = v
    @rotate.setter
    def rotate(self, v: int): self._rotate = v

    def __init__(self, mino_type: TetriminoDefine):
        """
        Args:
            mino_type: このテトリミノのタイプ定義
        """
        self._mino_type = mino_type
        self._n_rotate = len(mino_type.rotations)
        self._r = TETRIMINO_SPAWN_ROW
        self._c = TETRIMINO_SPAWN_COL
        self._rotate = 0

    def blocks(self) -> list[tuple[int, int]]:
        """現在の回転状態でのブロック座標を取得"""
        return [
            (self._r + dr, self._c + dc)
            for dr, dc in self._mino_type.rotations[self._rotate]
        ]


class TetriminoManager:
    """テトリミノの状態管理(アクティブ、ホールド、ゴースト)を担当するクラス

    Boardへの依存を持たず、衝突判定ロジックは外部から注入される。
    TetriminoSpawnerを保持し、7-bag方式でテトリミノを生成する。
    これによりテストが容易になり、疎結合な設計を実現する。
    """
    _spawner: TetriminoSpawner
    _active_mino: Tetrimino | None
    _hold_mino: Tetrimino | None
    _can_hold: bool

    def __init__(self):
        self._spawner = TetriminoSpawner()
        self._active_mino = self._create_new_tetrimino()
        self._hold_mino = None
        self._can_hold = True

    @property
    def active_mino(self) -> Tetrimino: return self._active_mino
    @property
    def hold_mino(self) -> Tetrimino | None: return self._hold_mino
    @property
    def can_hold(self) -> bool: return self._can_hold

    @property
    def next_mino(self) -> Tetrimino:
        """次に出現するテトリミノのプレビューを取得

        Returns:
            次に出現予定のテトリミノ（初期位置に配置された状態）
        """
        next_mino_type = self._spawner.peek_next_tetrimino_list(1)[0]
        return Tetrimino(next_mino_type)

    @property
    def next_minos(self) -> list[Tetrimino]:
        """次に出現する複数のテトリミノのプレビューを取得

        Returns:
            次に出現予定のテトリミノのリスト（3つ、初期位置に配置された状態）
        """
        next_mino_types = self._spawner.peek_next_tetrimino_list(3)
        return [Tetrimino(mino_type) for mino_type in next_mino_types]

    def _create_new_tetrimino(self) -> Tetrimino:
        """新しいテトリミノを生成

        Returns:
            初期位置に配置された新しいテトリミノ
        """
        mino_type = self._spawner.get_next_tetrimino()
        return Tetrimino(mino_type)

    def spawn(self, is_valid_position: callable) -> bool:
        """新しいテトリミノをスポーン

        Args:
            is_valid_position: テトリミノの位置が有効かを判定する関数

        Returns:
            スポーンに成功したらTrue、ゲームオーバーならFalse
        """
        self._active_mino = self._create_new_tetrimino()
        self._can_hold = True

        if not is_valid_position(self._active_mino):
            # NOTE: スポーンに失敗した場合は、ゲームオーバー
            #       アクティブミノはNoneにし、最終描画されないようにする
            self._active_mino = None
            return False

        return True

    def hold(self, is_valid_position: callable) -> bool:
        """ホールド機能を実行(アクティブミノとホールドミノを入れ替え)

        Args:
            is_valid_position: テトリミノの位置が有効かを判定する関数

        Returns:
            ホールド済みor成功したらTrue、ゲームオーバーならFalse
        """
        if not self._can_hold:
            return True

        if self._hold_mino is None:
            # 初回ホールド: アクティブミノをホールドし、新しいミノをスポーン
            self._hold_mino = copy.deepcopy(self._active_mino)
            self._active_mino = self._create_new_tetrimino()
        else:
            # 2回目以降: アクティブミノとホールドミノを入れ替え
            temp_mino = copy.deepcopy(self._active_mino)
            self._active_mino = copy.deepcopy(self._hold_mino)
            self._hold_mino = temp_mino

            # 入れ替えたアクティブミノを初期位置に移動
            self._active_mino.r = TETRIMINO_SPAWN_ROW
            self._active_mino.c = TETRIMINO_SPAWN_COL
            self._active_mino.rotate = 0
        
        # NOTE: ゲームオーバー直前にHoldすると、差し替えたテトリミノが置けない可能性がある
        if not is_valid_position(self._active_mino):
            # NOTE: ホールドに失敗した場合は、ゲームオーバー
            #       アクティブミノはNoneにし、最終描画されないようにする
            self._active_mino = None
            return False

        self._can_hold = False
        return True

    def create_ghost(self, is_valid_position: callable) -> Tetrimino | None:
        """ゴースト(落下予測位置)のテトリミノを作成

        Args:
            is_valid_position: テトリミノの位置が有効かを判定する関数

        Returns:
            ゴーストミノ。アクティブミノがない場合はNone
        """
        if not self._active_mino:
            return None

        ghost_mino = copy.deepcopy(self._active_mino)

        # 着地するまで下に移動
        while True:
            ghost_mino.r += 1

            # 衝突チェック
            original_r = self._active_mino.r
            self._active_mino.r = ghost_mino.r

            if not is_valid_position(self._active_mino):
                # 衝突したら1マス戻す
                ghost_mino.r -= 1
                self._active_mino.r = original_r
                break

            self._active_mino.r = original_r

        return ghost_mino
