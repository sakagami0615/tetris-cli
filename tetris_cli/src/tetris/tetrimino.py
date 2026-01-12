import random
from enum import Enum
from dataclasses import dataclass

from tetris_cli.src.common.color import Color


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
    MINO_O = TetriminoDefine(
        rotations = [
            [( 0,  0), ( 1,  0), ( 1,  1), ( 0,  1)],
        ],
        color = TETRIMINO_COLORS[MINO_O_INDEX],
    )
    MINO_I = TetriminoDefine(
        rotations = [
            [( 0,  0), ( 0, -1), ( 0,  1), ( 0,  2)],
            [( 0,  0), (-1,  0), ( 1,  0), ( 2,  0)],
        ],
        color = TETRIMINO_COLORS[MINO_I_INDEX],
    )
    MINO_L = TetriminoDefine(
        rotations = [
            [( 0,  0), ( 0, -1), ( 0,  1), ( 1,  1)],
            [( 0,  0), (-1,  0), ( 1,  0), ( 1, -1)],
            [( 0,  0), (-1, -1), ( 0, -1), ( 0,  1)],
            [( 0,  0), (-1,  0), ( 1,  0), (-1,  1)],
        ],
        color = TETRIMINO_COLORS[MINO_L_INDEX],
    )
    MINO_J = TetriminoDefine(
        rotations = [
            [( 0,  0), ( 0, -1), ( 0,  1), ( 1, -1)],
            [( 0,  0), (-1,  0), (-1, -1), ( 1,  0)],
            [( 0,  0), (-1,  1), ( 0, -1), ( 0,  1)],
            [( 0,  0), (-1,  0), ( 1,  0), ( 1,  1)],
        ],
        color = TETRIMINO_COLORS[MINO_J_INDEX],
    )
    MINO_S = TetriminoDefine(
        rotations = [
            [( 0,  0), ( 0,  1), ( 1, -1), ( 1,  0)],
            [( 0,  0), (-1,  0), ( 0,  1), ( 1,  1)],
        ],
        color = TETRIMINO_COLORS[MINO_S_INDEX],
    )
    MINO_Z = TetriminoDefine(
        rotations = [
            [( 0,  0), ( 0, -1), ( 1,  0), ( 1,  1)],
            [( 0,  0), (-1,  1), ( 0,  1), ( 1,  0)],
        ],
        color = TETRIMINO_COLORS[MINO_Z_INDEX],
    )
    MINO_T = TetriminoDefine(
        rotations = [
            [( 0,  0), ( 0, -1), ( 0,  1), ( 1,  0)],
            [( 0,  0), (-1,  0), ( 0, -1), ( 1,  0)],
            [( 0,  0), (-1,  0), ( 0, -1), ( 0,  1)],
            [( 0,  0), (-1,  0), ( 0,  1), ( 1,  0)],
        ],
        color = TETRIMINO_COLORS[MINO_T_INDEX],
    )


class TetriminoSpawner:
    """テトリミノのスポーン順序を管理するクラス

    7種類のテトリミノをランダムな順序で出現させる。
    全7種類が出現したら再度シャッフルして繰り返す（7-bag方式）。
    """
    _type_list: list[TetriminoDefine]

    _curr_index: int
    _n_type: int

    def __init__(self):
        self._type_list = [
            TetriminoType.MINO_O,
            TetriminoType.MINO_I,
            TetriminoType.MINO_L,
            TetriminoType.MINO_J,
            TetriminoType.MINO_S,
            TetriminoType.MINO_Z,
            TetriminoType.MINO_T,
        ]
        self._curr_index = -1
        self._n_type = len(self._type_list)

    def get_next_tetrimino(self) -> TetriminoDefine:
        """次のテトリミノタイプを取得

        7種類全てが出現したら、リストをシャッフルして新しいサイクルを開始する。
        """
        # テトリミノの出現順をシャッフル
        self._curr_index = (self._curr_index + 1) % self._n_type
        if self._curr_index == 0:
            random.shuffle(self._type_list)
        return self._type_list[self._curr_index].value



@dataclass
class ActiveTetrimino:
    """現在アクティブなテトリミノ"""
    r: int
    c: int
    mino_type: TetriminoDefine = None
    rotate: int = 0
    n_rotate: int = 0
    _spawner: TetriminoSpawner = TetriminoSpawner()

    def __post_init__(self):
        """初期化後にテトリミノをスポーン"""
        if self.mino_type is None:
            self.spawn(self.r, self.c)

    def spawn(self, init_r: int, init_c: int) -> None:
        """新しいテトリミノをスポーン"""
        self.mino_type = self._spawner.get_next_tetrimino()
        self.n_rotate = len(self.mino_type.rotations)
        self.r = init_r
        self.c = init_c
        self.rotate = 0

    def blocks(self) -> list[tuple[int, int]]:
        """現在の回転状態でのブロック座標を取得"""
        return [
            (self.r + dr, self.c + dc)
            for dr, dc in self.mino_type.rotations[self.rotate]
        ]
