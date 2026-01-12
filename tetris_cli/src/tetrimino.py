import random
from enum import Enum
from dataclasses import dataclass

from tetris_cli.src.color import Color


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


def get_tetrimino_type(mino_index: int) -> TetriminoDefine:
    """インデックスからテトリミノタイプを取得"""
    
    # テトリミノタイプのリスト（インデックスでアクセス）
    _TETRIMINO_TYPE_LIST = [
        TetriminoType.MINO_O,
        TetriminoType.MINO_I,
        TetriminoType.MINO_L,
        TetriminoType.MINO_J,
        TetriminoType.MINO_S,
        TetriminoType.MINO_Z,
        TetriminoType.MINO_T,
    ]

    if not 0 <= mino_index < N_TETRIMINO:
        raise IndexError(f"mino_index {mino_index} is out of range [0, {N_TETRIMINO})")
    return _TETRIMINO_TYPE_LIST[mino_index].value


@dataclass
class ActiveTetrimino:
    """現在アクティブなテトリミノ"""
    r: int
    c: int
    mino_type: TetriminoDefine = None
    rotate: int = 0
    n_rotate: int = 0

    def __post_init__(self):
        """初期化後にテトリミノをスポーン"""
        if self.mino_type is None:
            self.spawn(self.r, self.c)

    def spawn(self, init_r: int, init_c: int) -> None:
        """新しいテトリミノをスポーン"""
        mino_index = random.randrange(N_TETRIMINO)
        self.mino_type = get_tetrimino_type(mino_index)
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
