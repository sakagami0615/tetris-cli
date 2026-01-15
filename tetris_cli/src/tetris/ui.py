import copy
from dataclasses import dataclass

from tetris_cli.src.common import console

from tetris_cli.src.tetris.board import Board, CellType, BOARD_WALL_COLOR
from tetris_cli.src.tetris.tetrimino import Tetrimino
from tetris_cli.src.tetris.const import BOARD_WIDTH, BOARD_HEIGHT


@dataclass
class Pixel:
    """画面バッファの1ピクセル(1キャラクタ)を表す"""
    char: str = " "  # 表示文字(1文字分)
    color: tuple[int, int, int] = (255, 255, 255)  # RGB色


class ScreenBuffer:
    """画面バッファクラス - 画面全体をピクセル配列として管理"""

    def __init__(self, width: int, height: int):
        """
        Args:
            width: バッファの幅(文字数)
            height: バッファの高さ(行数)
        """
        self.width = width
        self.height = height
        # 2次元配列でバッファを初期化
        self.buffer: list[list[Pixel]] = [
            [Pixel() for _ in range(width)] for _ in range(height)
        ]

    def set_pixel(self, row: int, col: int, char: str, color: tuple[int, int, int] = (255, 255, 255)) -> None:
        """バッファの指定位置にピクセルを設定

        全角文字(2バイト文字)の場合は2ピクセル分を使用します。
        - col位置: 全角文字を格納
        - col+1位置: 空文字("")を格納(2バイト目のマーカー)

        Args:
            row: 行番号(0-indexed)
            col: 列番号(0-indexed)
            char: 表示文字(全角の場合は"■ "のように2文字、半角の場合は"a"のように1文字)
            color: RGB色
        """
        if not (0 <= row < self.height and 0 <= col < self.width):
            return

        # 全角文字(2文字)かどうかを判定
        if len(char) == 2:
            # 全角文字の場合: 1文字目を現在位置に、2文字目(通常は空白)を次の位置に
            self.buffer[row][col] = Pixel(char=char[0], color=color)
            if col + 1 < self.width:
                self.buffer[row][col + 1] = Pixel(char=char[1], color=color)
        else:
            # 半角文字の場合: そのまま設定
            self.buffer[row][col] = Pixel(char=char, color=color)

    def set_text(self, row: int, col: int, text: str, color: tuple[int, int, int] = (255, 255, 255)) -> None:
        """バッファの指定位置にテキストを設定

        Args:
            row: 行番号
            col: 開始列番号
            text: 表示テキスト
            color: RGB色
        """
        current_col = col
        for char in text:
            # 全角文字判定(簡易的に文字コードで判定)
            if ord(char) > 127:  # 全角文字
                # 全角文字は次の文字と組み合わせて2文字として扱う可能性があるが
                # ここでは1文字ずつ処理する(半角スペースを追加)
                self.set_pixel(row, current_col, char + " ", color)
                current_col += 2
            else:  # 半角文字
                self.set_pixel(row, current_col, char, color)
                current_col += 1

    def render(self) -> None:
        """画面に出力"""
        for row in self.buffer:
            for pixel in row:
                console.print_color(pixel.char, color=pixel.color, end="")
            console.print_color("")  # 改行


class Render:
    """ゲーム画面の描画を担当 - バッファ方式で描画"""

    # バッファサイズ
    RENDER_BUFFER_SIZE_ROW = 9 + 21                  # タイトルエリア + 盤面サイズ
    RENDER_BUFFER_SIZE_COL = 16 + 4 + 24 + 4 + 16    # ホールドエリア(8*2) + 余白(2*2) + 盤面サイズ(12*2) + 余白(2*2) + ホールドエリア(8*2)

    # 画面レイアウト定数
    TITLE_POS_ROW: int = 0
    TITLE_POS_COL: int = 2
    DESC_POS_ROW: int = 16
    DESC_POS_COL: int = 0
    BOARD_POS_ROW: int = 9
    BOARD_POS_COL: int = 16
    HOLD_POS_ROW: int = 8
    HOLD_POS_COL: int = 1
    NEXT_POS_ROW: int = 8
    NEXT_POS_COL: int = 43
    SCORE_POS_ROW: int = 28
    SCORE_POS_COL: int = 0

    def __init__(self):
        # 画面サイズを計算
        self.buffer = ScreenBuffer(self.RENDER_BUFFER_SIZE_COL, self.RENDER_BUFFER_SIZE_ROW)

    def _render_title(self) -> None:
        """タイトルをバッファに描画"""
        self.buffer.set_text(self.TITLE_POS_ROW,     self.TITLE_POS_COL, " __               __")
        self.buffer.set_text(self.TITLE_POS_ROW + 1, self.TITLE_POS_COL, "/\\ \\__           /\\ \\__           __")
        self.buffer.set_text(self.TITLE_POS_ROW + 2, self.TITLE_POS_COL, "\\ \\ ,_\\     __   \\ \\ ,_\\   _ __  /\\_\\     ____")
        self.buffer.set_text(self.TITLE_POS_ROW + 3, self.TITLE_POS_COL, " \\ \\ \\/   /'__`\\  \\ \\ \\/  /\\`'__\\\\/\\ \\   /',__\\")
        self.buffer.set_text(self.TITLE_POS_ROW + 4, self.TITLE_POS_COL, "  \\ \\ \\_ /\\  __/   \\ \\ \\_ \\ \\ \\/  \\ \\ \\ /\\__, `\\")
        self.buffer.set_text(self.TITLE_POS_ROW + 5, self.TITLE_POS_COL, "   \\ \\__\\\\ \\____\\   \\ \\__\\ \\ \\_\\   \\ \\_\\\\/\\____/")
        self.buffer.set_text(self.TITLE_POS_ROW + 6, self.TITLE_POS_COL, "    \\/__/ \\/____/    \\/__/  \\/_/    \\/_/ \\/___/")

    def _render_description(self) -> None:
        """操作説明をバッファに描画"""
        self.buffer.set_text(self.DESC_POS_ROW,     self.DESC_POS_COL, "<key>")
        self.buffer.set_text(self.DESC_POS_ROW + 1, self.DESC_POS_COL, "[←] left move")
        self.buffer.set_text(self.DESC_POS_ROW + 2, self.DESC_POS_COL, "[→] right move")
        self.buffer.set_text(self.DESC_POS_ROW + 3, self.DESC_POS_COL, "[x] cw rotate")
        self.buffer.set_text(self.DESC_POS_ROW + 4, self.DESC_POS_COL, "[z] ccw rotate")
        self.buffer.set_text(self.DESC_POS_ROW + 5, self.DESC_POS_COL, "[↑] hard drop")
        self.buffer.set_text(self.DESC_POS_ROW + 6, self.DESC_POS_COL, "[lshift] hold")
        self.buffer.set_text(self.DESC_POS_ROW + 7, self.DESC_POS_COL, "[q] quit")

    def _render_board(self, board: Board, ghost_mino: Tetrimino | None, active_mino: Tetrimino | None) -> None:
        """ボード(盤面)をバッファに描画

        Args:
            board: ゲームボード
            ghost_mino: ゴーストミノ
            active_mino: アクティブミノ
        """

        # 盤面の開始位置
        start_row = self.BOARD_POS_ROW
        start_col = self.BOARD_POS_COL

        # ボードのコピーを作成してミノを重ね合わせ
        cells = copy.deepcopy(board.cells)

        # ゴーストを重ね合わせ(下層)
        if ghost_mino:
            for r, c in ghost_mino.blocks():
                if cells[r][c].cell_type == CellType.EMPTY:
                    cells[r][c].cell_type = CellType.GHOST
                    original_color = ghost_mino.mino_type.color
                    cells[r][c].color = tuple(int(v * 0.5) for v in original_color)

        # アクティブミノを重ね合わせ(上層)
        if active_mino:
            for r, c in active_mino.blocks():
                cells[r][c].cell_type = CellType.MINO
                cells[r][c].color = active_mino.mino_type.color

        # バッファに描画(全角文字は2ピクセル幅なのでcol*2で配置)
        for r in range(1, BOARD_HEIGHT + 2):
            for c in range(BOARD_WIDTH + 2):
                cell = cells[r][c]
                buffer_row = start_row + (r - 1)
                buffer_col = start_col + c * 2  # 全角文字は2ピクセル幅

                # セルタイプに応じて文字と色を決定
                if cell.cell_type == CellType.EMPTY:
                    char = "  "
                    color = (255, 255, 255)
                elif cell.cell_type == CellType.GHOST:
                    char = "□ "
                    color = cell.color
                else:
                    char = "■ "
                    color = cell.color

                self.buffer.set_pixel(buffer_row, buffer_col, char, color)

    def _render_hold_area(self, hold_mino: Tetrimino | None) -> None:
        """ホールドエリアをバッファに描画

        Args:
            hold_mino: ホールド中のミノ
        """
        self.buffer.set_text(self.HOLD_POS_ROW, self.HOLD_POS_COL, "HOLD")

        # ホールドエリアの開始位置
        start_row = self.HOLD_POS_ROW + 1
        start_col = self.HOLD_POS_COL

        # ホールドエリアの枠を描画(6x6、全角文字は2ピクセル幅)
        # 上部の壁
        for i in range(6):
            self.buffer.set_pixel(start_row, start_col + i * 2, "■ ", BOARD_WALL_COLOR)

        # 中央4行(左右の壁 + 中身)
        for i in range(4):
            row = start_row + 1 + i
            # 左の壁
            self.buffer.set_pixel(row, start_col, "■ ", BOARD_WALL_COLOR)
            # 右の壁
            self.buffer.set_pixel(row, start_col + 5 * 2, "■ ", BOARD_WALL_COLOR)

        # 下部の壁
        for i in range(6):
            self.buffer.set_pixel(start_row + 5, start_col + i * 2, "■ ", BOARD_WALL_COLOR)

        # ホールドミノを描画
        if hold_mino:
            blocks = hold_mino.mino_type.rotations[0]
            center_r, center_c = 2, 1  # 4x4グリッド内の中心
            color = hold_mino.mino_type.color

            for dr, dc in blocks:
                r = center_r + dr
                c = center_c + dc
                if 0 <= r < 4 and 0 <= c < 4:
                    buffer_row = start_row + 1 + r
                    buffer_col = start_col + (1 + c) * 2  # 全角文字は2ピクセル幅
                    self.buffer.set_pixel(buffer_row, buffer_col, "■ ", color)

    def _render_next_area(self, next_minos: list[Tetrimino]) -> None:
        """ネクストエリアをバッファに描画

        Args:
            next_minos: 次に出現するミノのリスト（最大3つ）
        """
        self.buffer.set_text(self.NEXT_POS_ROW, self.NEXT_POS_COL, "NEXT")

        # 3つのネクストミノを縦に並べて描画
        for idx, next_mino in enumerate(next_minos[:3]):
            # 各ネクストエリアの開始位置（7行ごとに配置）
            start_row = self.NEXT_POS_ROW + 1 + idx * 7
            start_col = self.NEXT_POS_COL

            # ネクストエリアの枠を描画(6x6、全角文字は2ピクセル幅)
            # 上部の壁
            for i in range(6):
                self.buffer.set_pixel(start_row, start_col + i * 2, "■ ", BOARD_WALL_COLOR)

            # 中央4行(左右の壁 + 中身)
            for i in range(4):
                row = start_row + 1 + i
                # 左の壁
                self.buffer.set_pixel(row, start_col, "■ ", BOARD_WALL_COLOR)
                # 右の壁
                self.buffer.set_pixel(row, start_col + 5 * 2, "■ ", BOARD_WALL_COLOR)

            # 下部の壁
            for i in range(6):
                self.buffer.set_pixel(start_row + 5, start_col + i * 2, "■ ", BOARD_WALL_COLOR)

            # ネクストミノを描画
            if next_mino:
                blocks = next_mino.mino_type.rotations[0]
                center_r, center_c = 2, 1  # 4x4グリッド内の中心
                color = next_mino.mino_type.color

                for dr, dc in blocks:
                    r = center_r + dr
                    c = center_c + dc
                    if 0 <= r < 4 and 0 <= c < 4:
                        buffer_row = start_row + 1 + r
                        buffer_col = start_col + (1 + c) * 2  # 全角文字は2ピクセル幅
                        self.buffer.set_pixel(buffer_row, buffer_col, "■ ", color)

    def _render_score(self, score: int) -> None:
        """フッター(スコア)をバッファに描画

        Args:
            score: 現在のスコア
        """
        self.buffer.set_text(self.SCORE_POS_ROW,     self.SCORE_POS_COL, "<score>")
        self.buffer.set_text(self.SCORE_POS_ROW + 1, self.SCORE_POS_COL, f"{score}")

    def draw(self, board: Board, active_mino: Tetrimino | None, ghost_mino: Tetrimino | None,
             hold_mino: Tetrimino | None, next_minos: list[Tetrimino], score: int = 0, is_cursor_up: bool = True) -> None:
        """ゲーム画面を描画

        Args:
            board: ゲームボード
            active_mino: アクティブミノ
            ghost_mino: ゴーストミノ
            hold_mino: ホールド中のミノ
            next_minos: 次に出現するミノのリスト（最大3つ）
            score: スコア
            is_cursor_up: カーソルを上に戻すか
        """
        # バッファをクリア
        self.buffer = ScreenBuffer(self.buffer.width, self.buffer.height)

        # 各要素をバッファに描画
        self._render_title()
        self._render_description()
        self._render_board(board, ghost_mino, active_mino)
        self._render_hold_area(hold_mino)
        self._render_next_area(next_minos)
        self._render_score(score)

        self.buffer.render()

        # カーソルを上に戻す
        if is_cursor_up:
            console.cursor_up(self.buffer.height)
