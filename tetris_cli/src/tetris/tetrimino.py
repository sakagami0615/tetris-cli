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


class ActiveTetrimino:
    """現在アクティブなテトリミノ"""
    _mino_type: TetriminoDefine
    _r: int
    _c: int
    _rotate: int = 0
    _n_rotate: int = 0
    _spawner: TetriminoSpawner = TetriminoSpawner()

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

    def __init__(self):
        self.spawn()
    
    def init_pos(self) -> None:
        """初期位置にテトリミノを移動"""
        self._r = TETRIMINO_SPAWN_ROW 
        self._c = TETRIMINO_SPAWN_COL
        self._rotate = 0

    def spawn(self) -> None:
        """新しいテトリミノをスポーン"""
        self._mino_type = self._spawner.get_next_tetrimino()
        self._n_rotate = len(self._mino_type.rotations)
        self.init_pos()

    def blocks(self) -> list[tuple[int, int]]:
        """現在の回転状態でのブロック座標を取得"""
        return [
            (self._r + dr, self._c + dc)
            for dr, dc in self._mino_type.rotations[self._rotate]
        ]
