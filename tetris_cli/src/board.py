import copy

from tetris_cli.src.color import Color
from tetris_cli.src.tetrimino import ActiveTetrimino
from tetris_cli.src.const import BOARD_WIDTH, BOARD_HEIGHT


BOARD_WALL = -2
BOARD_EMPTY = -1

BOARD_WALL_COLOR = Color.GRAY.value


class Cell:
    wall: bool = False
    fill: bool = False
    color: tuple[int, int, int] = (0, 0, 0)


class Board:
    cells: list[list[Cell]]

    def _create_cells(self) -> list[list[Cell]]:
        cells: list[list[Cell]] = []
        for r in range(BOARD_HEIGHT + 2):
            cells.append([])
            for c in range(BOARD_WIDTH + 2):
                cells[-1].append(Cell())

        for r in range(BOARD_HEIGHT + 2):
            cells[r][0].wall = True
            cells[r][0].fill = True
            cells[r][0].color = BOARD_WALL_COLOR
            cells[r][-1].wall = True
            cells[r][-1].fill = True
            cells[r][-1].color = BOARD_WALL_COLOR
        for c in range(BOARD_WIDTH + 2):
            cells[-1][c].wall = True
            cells[-1][c].fill = True
            cells[-1][c].color = BOARD_WALL_COLOR
        return cells

    def __init__(self):
        self.cells = self._create_cells()
    
    def write_tetrimino(self, active_mino: ActiveTetrimino) -> None:
        for r, c in active_mino.blocks():
            self.cells[r][c].fill = True
            self.cells[r][c].color = active_mino.mino_type.color

    def clear_fill_lines(self) -> None:
        def is_fill_line(row):
            for c in range(1, BOARD_WIDTH + 1):
                cell = self.cells[row][c]
                if not cell.fill or cell.wall:
                    return False
            return True
        
        def drop_lines(row):
            for r in range(row, 0, -1):
                for c in range(1, BOARD_WIDTH + 1):
                    self.cells[r][c] = copy.deepcopy(self.cells[r - 1][c])
        
        row = BOARD_HEIGHT + 1
        while row > 0:
            if is_fill_line(row):
                drop_lines(row)
            else:
                row -= 1
