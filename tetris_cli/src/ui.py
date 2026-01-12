import copy

from tetris_cli.src import console
from tetris_cli.src.board import Board, CellType
from tetris_cli.src.tetrimino import ActiveTetrimino
from tetris_cli.src.const import BOARD_WIDTH, BOARD_HEIGHT, RENDER_ROW_OFFSET


class Render:
    """ゲーム画面の描画を担当"""

    def _overlay_ghost_mino(self, cells: list[list], ghost_mino: ActiveTetrimino) -> None:
        """ゴースト（落下予測位置）をセルに重ね合わせる"""
        # ゴーストのブロックを配置
        for r, c in ghost_mino.blocks():
            # まだ埋まっていないセルにのみゴーストを表示
            if cells[r][c].cell_type == CellType.EMPTY:
                cells[r][c].cell_type = CellType.GHOST
                # ゴーストは元の色を暗くして表示
                original_color = ghost_mino.mino_type.color
                cells[r][c].color = tuple(int(v * 0.5) for v in original_color)  # 50%の明度

    def _overlay_active_mino(self, cells: list[list], active_mino: ActiveTetrimino) -> None:
        """アクティブなテトリミノをセルに重ね合わせる"""
        for r, c in active_mino.blocks():
            cells[r][c].cell_type = CellType.MINO
            cells[r][c].color = active_mino.mino_type.color

    def _draw_cell(self, cell) -> None:
        """1セルを描画"""
        if cell.cell_type == CellType.EMPTY:
            console.print_color("  ", end="")
        elif cell.cell_type == CellType.GHOST:
            # ゴーストは枠線のみ表示
            console.print_color("□ ", color=cell.color, end="")
        else:
            # 壁またはミノは塗りつぶし
            console.print_color("■ ", color=cell.color, end="")

    def _draw_board(self, cells: list[list]) -> None:
        """ボード全体を描画"""
        for r in range(RENDER_ROW_OFFSET, BOARD_HEIGHT + 2):
            for c in range(BOARD_WIDTH + 2):
                self._draw_cell(cells[r][c])
            console.print_color("")

    def draw(self, board: Board, active_mino: ActiveTetrimino | None, ghost_mino: ActiveTetrimino | None, is_cursor_up: bool = True) -> None:
        """ゲーム画面を描画"""
        # ボードのコピーを作成
        cells = copy.deepcopy(board.cells)

        # ゴーストとアクティブなテトリミノを重ね合わせ
        # 先にゴーストを描画（下層）
        if ghost_mino:
            self._overlay_ghost_mino(cells, ghost_mino)
        if active_mino:
            # 次にアクティブなテトリミノを描画（上層）
            self._overlay_active_mino(cells, active_mino)

        # 描画
        self._draw_board(cells)

        # カーソルを上に戻す
        if is_cursor_up:
            console.cursor_up(BOARD_HEIGHT + 1)
