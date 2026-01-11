import copy

from tetris_cli.src import console
from tetris_cli.src.board import Board
from tetris_cli.src.tetrimino import ActiveTetrimino
from tetris_cli.src.const import BOARD_WIDTH, BOARD_HEIGHT


class Render:

    def draw(self, board: Board, active_mino: ActiveTetrimino | None, is_cursor_up: bool = True) -> None:
        cells = copy.deepcopy(board.cells)

        if active_mino:
            for r, c in active_mino.blocks():
                cells[r][c].fill = True
                cells[r][c].color = active_mino.mino_type.color

        for r in range(1, BOARD_HEIGHT + 2):
            for c in range(BOARD_WIDTH + 2):
                cell = cells[r][c]
                if not cell.fill:
                    console.print_color("  ", end="")
                else:
                    console.print_color("■ ", color=cell.color, end="")
            console.print_color("")
        if is_cursor_up:
            console.cursor_up(BOARD_HEIGHT + 1)
