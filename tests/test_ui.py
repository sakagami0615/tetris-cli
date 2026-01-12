import pytest
from unittest.mock import patch, MagicMock
from tetris_cli.src.tetris.ui import Render
from tetris_cli.src.tetris.board import Board, Cell, CellType
from tetris_cli.src.tetris.tetrimino import ActiveTetrimino, TetriminoType

@pytest.fixture
def render():
    return Render()

@patch('tetris_cli.src.common.console.print_color')
@patch('tetris_cli.src.common.console.cursor_up')
def test_draw(mock_cursor_up, mock_print_color, render):
    board = Board()
    active_mino = ActiveTetrimino()
    ghost_mino = ActiveTetrimino()
    hold_mino = ActiveTetrimino()
    
    # 描画メソッドを実行（エラーが出ないことを確認）
    render.draw(board, active_mino, ghost_mino, hold_mino, score=100)
    
    # printが呼ばれたか確認
    assert mock_print_color.called
    assert mock_cursor_up.called

@patch('tetris_cli.src.common.console.print_color')
def test_draw_cell_types(mock_print_color, render):
    """各セルタイプの描画テスト（カバレッジ向上）"""
    render._draw_cell(Cell(cell_type=CellType.EMPTY))
    render._draw_cell(Cell(cell_type=CellType.WALL))
    render._draw_cell(Cell(cell_type=CellType.MINO))
    render._draw_cell(Cell(cell_type=CellType.GHOST))
    
    assert mock_print_color.call_count == 4

def test_create_hold_display_grid(render):
    # Noneの場合
    grid = render._create_hold_display_grid(None)
    assert not any(any(row) for row in grid)
    
    # O-Minoの場合 (2x2ブロック)
    # Rotations[0] = [(0,0), (-1,0), (-1,1), (0,1)]
    # 中心(2,1)に対して配置される
    mino = ActiveTetrimino()
    # 強制的にO型にする
    object.__setattr__(mino, '_mino_type', TetriminoType.MINO_O)
    # mino_type をモック化して rotations 属性を持たせる
    mock_mino_type = MagicMock()
    mock_mino_type.rotations = [[(0,0), (-1,0), (-1,1), (0,1)]]
    object.__setattr__(mino, '_mino_type', mock_mino_type)

    grid = render._create_hold_display_grid(mino)
    # グリッド内にTrueがあるか確認
    assert grid[2][1]
    assert grid[1][1]
    assert grid[1][2]
    assert grid[2][2]