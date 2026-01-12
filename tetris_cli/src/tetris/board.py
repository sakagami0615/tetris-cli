import copy
from dataclasses import dataclass, field
from enum import Enum

from tetris_cli.src.common.color import Color

from tetris_cli.src.tetris.tetrimino import ActiveTetrimino
from tetris_cli.src.tetris.const import BOARD_WIDTH, BOARD_HEIGHT


BOARD_WALL_COLOR = Color.GRAY.value


class CellType(Enum):
    EMPTY: int = 0
    WALL: int = 1
    GHOST: int = 2
    MINO: int = 3


@dataclass
class Cell:
    """ボードの1セルを表すデータクラス"""
    cell_type: CellType = CellType.EMPTY
    color: tuple[int, int, int] = field(default_factory=lambda: (0, 0, 0))

    @property
    def wall(self) -> bool:
        """壁かどうか"""
        return self.cell_type == CellType.WALL

    @property
    def fill(self) -> bool:
        """埋まっているかどうか（壁またはミノ）"""
        return self.cell_type in (CellType.WALL, CellType.MINO, CellType.GHOST)


class Board:
    cells: list[list[Cell]]

    @staticmethod
    def _create_wall_cell() -> Cell:
        """壁セルを作成"""
        return Cell(cell_type=CellType.WALL, color=BOARD_WALL_COLOR)

    def _create_cells(self) -> list[list[Cell]]:
        """ボードのセルを初期化（壁を含む）"""
        cells = [
            [Cell(cell_type=CellType.EMPTY) for _ in range(BOARD_WIDTH + 2)]
            for _ in range(BOARD_HEIGHT + 2)
        ]

        # 左右の壁
        for r in range(BOARD_HEIGHT + 2):
            cells[r][0] = self._create_wall_cell()
            cells[r][-1] = self._create_wall_cell()

        # 下の壁
        for c in range(BOARD_WIDTH + 2):
            cells[-1][c] = self._create_wall_cell()

        return cells

    def __init__(self):
        self.cells = self._create_cells()
    
    def write_tetrimino(self, active_mino: ActiveTetrimino) -> None:
        """テトリミノをボードに書き込む"""
        for r, c in active_mino.blocks():
            self.cells[r][c].cell_type = CellType.MINO
            self.cells[r][c].color = active_mino.mino_type.color

    def _is_fill_line(self, row: int) -> bool:
        """指定行が埋まっているかチェック"""
        for c in range(1, BOARD_WIDTH + 1):
            cell = self.cells[row][c]
            if not cell.fill or cell.wall:
                return False
        return True

    def _drop_lines(self, row: int) -> None:
        """指定行以上のラインを1つ下に落とす"""
        for r in range(row, 0, -1):
            for c in range(1, BOARD_WIDTH + 1):
                self.cells[r][c] = copy.deepcopy(self.cells[r - 1][c])

    def clear_fill_lines(self) -> int:
        """埋まった行をクリアして、クリアした行数を返す"""
        cleared_lines = 0
        row = BOARD_HEIGHT + 1
        while row > 0:
            if self._is_fill_line(row):
                self._drop_lines(row)
                cleared_lines += 1
            else:
                row -= 1
        return cleared_lines
