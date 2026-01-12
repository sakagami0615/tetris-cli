import copy

from tetris_cli.src import console
from tetris_cli.src.board import Board, CellType, BOARD_WALL_COLOR
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

    def _create_hold_display_grid(self, hold_mino: ActiveTetrimino | None) -> list[list[bool]]:
        """ホールドミノの表示用グリッド（4x4）を作成"""
        # 4x4のグリッドを作成（False = 空、True = ブロック）
        grid = [[False for _ in range(4)] for _ in range(4)]

        if hold_mino is None:
            return grid

        # ホールドミノの最初の回転（rotate=0）のブロック配置を取得
        blocks = hold_mino.mino_type.rotations[0]

        # 中心を(1, 1)として配置（4x4グリッドの中心）
        center_r, center_c = 1, 1
        for dr, dc in blocks:
            r = center_r + dr
            c = center_c + dc
            if 0 <= r < 4 and 0 <= c < 4:
                grid[r][c] = True

        return grid

    def _draw_field(self, cells: list[list], hold_mino: ActiveTetrimino | None) -> None:
        """ボード全体を描画（ホールド情報を右側に表示）"""
        # タイトル行を描画
        console.print_color("←→:move,xz:rot")
        console.print_color("↑:harddrop,lshift:hold", end="")
        console.print_color(" " * 4 + "HOLD")

        # ホールドミノのグリッドを作成
        hold_grid = self._create_hold_display_grid(hold_mino)
        hold_color = hold_mino.mino_type.color if hold_mino else (128, 128, 128)

        row_index = 0
        for r in range(RENDER_ROW_OFFSET, BOARD_HEIGHT + 2):
            # ボードを描画
            for c in range(BOARD_WIDTH + 2):
                self._draw_cell(cells[r][c])

            # ホールドエリアを右側に表示
            if row_index == 0:
                # 上部の壁（6ブロック幅 = 4マス + 左右の壁）
                console.print_color("  ", end="")
                for _ in range(6):
                    console.print_color("■ ", color=BOARD_WALL_COLOR, end="")
            elif 1 <= row_index <= 4:
                # 左の壁 + ホールドミノ + 右の壁
                console.print_color("  ", end="")
                console.print_color("■ ", color=BOARD_WALL_COLOR, end="")
                for col in range(4):
                    if hold_grid[row_index - 1][col]:
                        console.print_color("■ ", color=hold_color, end="")
                    else:
                        console.print_color("  ", end="")
                console.print_color("■ ", color=BOARD_WALL_COLOR, end="")
            elif row_index == 5:
                # 下部の壁（6ブロック幅）
                console.print_color("  ", end="")
                for _ in range(6):
                    console.print_color("■ ", color=BOARD_WALL_COLOR, end="")

            console.print_color("")
            row_index += 1
        score = 0
        console.print_color(f"score: {score}")

    def draw(self, board: Board, active_mino: ActiveTetrimino | None, ghost_mino: ActiveTetrimino | None, hold_mino: ActiveTetrimino | None, is_cursor_up: bool = True) -> None:
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
        self._draw_field(cells, hold_mino)

        # カーソルを上に戻す（タイトル行 + ボード行）
        if is_cursor_up:
            console.cursor_up(BOARD_HEIGHT + 4)
