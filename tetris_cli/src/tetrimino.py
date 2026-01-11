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
    if mino_index == MINO_O_INDEX:
        return TetriminoType.MINO_O.value
    elif mino_index == MINO_I_INDEX:
        return TetriminoType.MINO_I.value
    elif mino_index == MINO_L_INDEX:
        return TetriminoType.MINO_L.value
    elif mino_index == MINO_J_INDEX:
        return TetriminoType.MINO_J.value
    elif mino_index == MINO_S_INDEX:
        return TetriminoType.MINO_S.value
    elif mino_index == MINO_Z_INDEX:
        return TetriminoType.MINO_Z.value
    elif mino_index == MINO_T_INDEX:
        return TetriminoType.MINO_T.value
    else:
        raise IndexError("mino_index is out of range")


class ActiveTetrimino:
    mino_type: TetriminoDefine
    n_rotate: int
    rotate: int
    r: int
    c: int

    def __init__(self, init_r: int, init_c: int):
        self.spawn(init_r, init_c)

    def spawn(self, init_r: int, init_c: int) -> None:
        mino_index = random.randrange(N_TETRIMINO)
        self.mino_type = get_tetrimino_type(mino_index)
        self.n_rotate = len(self.mino_type.rotations)
        self.r = init_r
        self.c = init_c
        self.rotate = 0

    def blocks(self) -> list[tuple[int, int]]:
        return [
            (self.r + dr, self.c + dc)
            for dr, dc in self.mino_type.rotations[self.rotate]
        ]
