import pytest
from tetris_cli.src.tetris.board import Board, CellType
from tetris_cli.src.tetris.const import BOARD_WIDTH, BOARD_HEIGHT

@pytest.fixture
def board():
    return Board()

def test_initial_board_structure(board):
    """ボードの初期構造（壁と空セル）を確認"""
    # 左の壁
    assert board.cells[0][0].cell_type == CellType.WALL
    # 右の壁
    assert board.cells[0][BOARD_WIDTH + 1].cell_type == CellType.WALL
    # 下の壁
    assert board.cells[BOARD_HEIGHT + 1][1].cell_type == CellType.WALL
    # 内部は空
    assert board.cells[1][1].cell_type == CellType.EMPTY

def test_clear_fill_lines(board):
    """ライン消去のロジックを確認"""
    # 最下行（壁のすぐ上）を埋める
    target_row = BOARD_HEIGHT
    for c in range(1, BOARD_WIDTH + 1):
        board.cells[target_row][c].cell_type = CellType.MINO
    
    # その上の行に1つだけブロックを置く（落下確認用）
    board.cells[target_row - 1][1].cell_type = CellType.MINO

    # ライン消去実行
    cleared_lines = board.clear_fill_lines()

    # 1行消えているはず
    assert cleared_lines == 1
    
    # 消えた行は上の行が落ちてくるので、(target_row, 1) にブロックがあるはず
    assert board.cells[target_row][1].cell_type == CellType.MINO
    # 元の場所は空になっているはず
    assert board.cells[target_row - 1][1].cell_type == CellType.EMPTY

def test_is_fill_line_false(board):
    """埋まっていない行の判定"""
    target_row = BOARD_HEIGHT
    # 1つだけ空ける
    for c in range(1, BOARD_WIDTH):
        board.cells[target_row][c].cell_type = CellType.MINO
    
    assert not board._is_fill_line(target_row)