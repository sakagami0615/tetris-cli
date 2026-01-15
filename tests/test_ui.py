import pytest
from unittest.mock import patch
from tetris_cli.src.tetris.ui import Render, ScreenBuffer, Pixel
from tetris_cli.src.tetris.board import Board
from tetris_cli.src.tetris.tetrimino import Tetrimino, TetriminoType

@pytest.fixture
def render():
    return Render()

@patch('tetris_cli.src.common.console.print_color')
@patch('tetris_cli.src.common.console.cursor_up')
def test_draw(mock_cursor_up, mock_print_color, render):
    board = Board()
    active_mino = Tetrimino(TetriminoType.MINO_O.value)
    ghost_mino = Tetrimino(TetriminoType.MINO_I.value)
    hold_mino = Tetrimino(TetriminoType.MINO_T.value)
    next_minos = [
        Tetrimino(TetriminoType.MINO_L.value),
        Tetrimino(TetriminoType.MINO_J.value),
        Tetrimino(TetriminoType.MINO_S.value),
    ]

    # 描画メソッドを実行（エラーが出ないことを確認）
    render.draw(board, active_mino, ghost_mino, hold_mino, next_minos, score=100)

    # printが呼ばれたか確認
    assert mock_print_color.called
    assert mock_cursor_up.called

def test_screen_buffer():
    """ScreenBufferクラスのテスト"""
    buffer = ScreenBuffer(10, 5)

    # バッファサイズの確認
    assert buffer.width == 10
    assert buffer.height == 5
    assert len(buffer.buffer) == 5
    assert len(buffer.buffer[0]) == 10

    # ピクセル設定のテスト(全角文字は2ピクセルに分割される)
    buffer.set_pixel(0, 0, "■ ", (255, 0, 0))
    assert buffer.buffer[0][0].char == "■"  # 1文字目
    assert buffer.buffer[0][1].char == " "  # 2文字目(空白)
    assert buffer.buffer[0][0].color == (255, 0, 0)
    assert buffer.buffer[0][1].color == (255, 0, 0)

    # テキスト設定のテスト
    buffer.set_text(1, 0, "TEST")
    assert buffer.buffer[1][0].char == "T"
    assert buffer.buffer[1][1].char == "E"
    assert buffer.buffer[1][2].char == "S"
    assert buffer.buffer[1][3].char == "T"

    # 範囲外のピクセル設定テスト
    buffer.set_pixel(-1, 0, "X", (0, 0, 0))  # 範囲外（行が負）
    buffer.set_pixel(0, -1, "X", (0, 0, 0))  # 範囲外（列が負）
    buffer.set_pixel(100, 0, "X", (0, 0, 0))  # 範囲外（行が大きすぎ）
    buffer.set_pixel(0, 100, "X", (0, 0, 0))  # 範囲外（列が大きすぎ）
    # エラーが発生せず、バッファが変更されていないことを確認
    assert buffer.buffer[0][0].char == "■"  # 最初のテストで設定された値のまま

@patch('tetris_cli.src.common.console.print_color')
def test_render_methods(mock_print_color, render):
    """各レンダリングメソッドのテスト"""
    board = Board()
    active_mino = Tetrimino(TetriminoType.MINO_O.value)
    hold_mino = Tetrimino(TetriminoType.MINO_T.value)

    # タイトル描画テスト
    render._render_title()
    # タイトルが描画されていることを確認（アンダースコアがあるはず）
    assert any(
        pixel.char == "_" for row in render.buffer.buffer[:7] for pixel in row
    )

    # ボード描画テスト
    render._render_board(board, None, active_mino)
    # バッファにデータが書き込まれていることを確認(全角文字は1文字目のみ)
    assert any(
        pixel.char == "■" for row in render.buffer.buffer for pixel in row
    )

    # ホールドエリア描画テスト
    render._render_hold_area(hold_mino)
    # ホールドエリアが描画されていることを確認
    # HOLD_POS_ROW (8) から始まる
    hold_start = render.HOLD_POS_ROW + 1
    assert any(
        pixel.char == "■" for row in render.buffer.buffer[hold_start:hold_start+6] for pixel in row
    )

    # スコア描画テスト
    render._render_score(1000)
    # スコアが描画されていることを確認(SCORE_POS_ROWとその次の行)
    score_rows = render.buffer.buffer[render.SCORE_POS_ROW:render.SCORE_POS_ROW + 2]
    assert any(
        pixel.char in ["s", "c", "o", "r", "e", "1", "0"]
        for row in score_rows for pixel in row
    )

    # ネクストエリア描画テスト（3つ）
    next_minos = [
        Tetrimino(TetriminoType.MINO_L.value),
        Tetrimino(TetriminoType.MINO_J.value),
        Tetrimino(TetriminoType.MINO_S.value),
    ]
    render._render_next_area(next_minos)
    # ネクストエリアが描画されていることを確認（3つのエリア分）
    # NEXT_POS_ROW (8) から始まり、7行ごとに配置
    next_start = render.NEXT_POS_ROW + 1
    assert any(
        pixel.char == "■" for row in render.buffer.buffer[next_start:next_start+6] for pixel in row
    )
    assert any(
        pixel.char == "■" for row in render.buffer.buffer[next_start+7:next_start+13] for pixel in row
    )
    assert any(
        pixel.char == "■" for row in render.buffer.buffer[next_start+14:next_start+20] for pixel in row
    )