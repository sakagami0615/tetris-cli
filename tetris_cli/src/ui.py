import copy

from tetris_cli.src import console
from tetris_cli.src.board import Board
from tetris_cli.src.tetrimino import ActiveTetrimino
from tetris_cli.src.const import BOARD_WIDTH, BOARD_HEIGHT, RENDER_ROW_OFFSET


class Render:
    """ゲーム画面の描画を担当"""

    def _overlay_active_mino(self, cells: list[list], active_mino: ActiveTetrimino) -> None:
        """アクティブなテトリミノをセルに重ね合わせる"""
        for r, c in active_mino.blocks():
            cells[r][c].fill = True
            cells[r][c].color = active_mino.mino_type.color

    def _draw_cell(self, cell) -> None:
        """1セルを描画"""
        if not cell.fill:
            console.print_color("  ", end="")
        else:
            console.print_color("■ ", color=cell.color, end="")

    def _draw_board(self, cells: list[list]) -> None:
        """ボード全体を描画"""
        for r in range(RENDER_ROW_OFFSET, BOARD_HEIGHT + 2):
            for c in range(BOARD_WIDTH + 2):
                self._draw_cell(cells[r][c])
            console.print_color("")

    def draw(self, board: Board, active_mino: ActiveTetrimino | None, is_cursor_up: bool = True) -> None:
        """ゲーム画面を描画"""
        # ボードのコピーを作成
        cells = copy.deepcopy(board.cells)

        # アクティブなテトリミノを重ね合わせ
        if active_mino:
            self._overlay_active_mino(cells, active_mino)

        # 描画
        self._draw_board(cells)

        # カーソルを上に戻す
        if is_cursor_up:
            console.cursor_up(BOARD_HEIGHT + 1)
