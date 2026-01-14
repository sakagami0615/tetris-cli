import pytest
from tetris_cli.src.tetris.tetrimino import Tetrimino, TetriminoManager, TetriminoType
from tetris_cli.src.tetris.board import Board

@pytest.fixture
def tetrimino_manager():
    return TetriminoManager()

@pytest.fixture
def board():
    return Board()

def test_tetrimino_hold_swap(tetrimino_manager, board):
    """ホールド入れ替え時の初期位置設定テスト"""
    def is_valid_position(mino):
        for r, c in mino.blocks():
            cell = board.cells[r][c]
            if cell.fill:
                return False
        return True

    # 初回ホールド
    first_mino = tetrimino_manager.active_mino
    first_mino_type = first_mino.mino_type
    tetrimino_manager.hold(is_valid_position)

    assert tetrimino_manager.hold_mino is not None
    assert tetrimino_manager.hold_mino.mino_type == first_mino_type

    # アクティブミノを移動させる
    tetrimino_manager.active_mino.r = 10
    tetrimino_manager.active_mino.c = 7
    tetrimino_manager.active_mino.rotate = 1

    # 再度ホールドできるようにする
    tetrimino_manager._can_hold = True

    # 2回目のホールド（入れ替え） -> 初期位置にリセットされるはず
    tetrimino_manager.hold(is_valid_position)

    # 入れ替え後のアクティブミノは初期位置にいるはず
    assert tetrimino_manager.active_mino.r == 1  # TETRIMINO_SPAWN_ROW
    assert tetrimino_manager.active_mino.c == 5  # TETRIMINO_SPAWN_COL
    assert tetrimino_manager.active_mino.rotate == 0

def test_ghost_mino_loop(tetrimino_manager, board):
    """ゴーストミノ作成のループ処理テスト"""
    def is_valid_position(mino):
        for r, c in mino.blocks():
            cell = board.cells[r][c]
            if cell.fill:
                return False
        return True

    # アクティブミノを少し下に移動
    tetrimino_manager.active_mino.r = 5

    # ゴーストミノを作成
    ghost = tetrimino_manager.create_ghost(is_valid_position)

    # ゴーストはアクティブミノより下にいるはず
    assert ghost is not None
    assert ghost.r > tetrimino_manager.active_mino.r

    # ゴーストの位置は有効な位置の1つ上（衝突する位置の1つ前）のはず
    ghost.r += 1
    # この位置は衝突するはず
    original_r = tetrimino_manager.active_mino.r
    tetrimino_manager.active_mino.r = ghost.r
    assert not is_valid_position(tetrimino_manager.active_mino)
    tetrimino_manager.active_mino.r = original_r

def test_ghost_mino_none(tetrimino_manager, board):
    """アクティブミノがNoneの場合のゴースト作成テスト"""
    def is_valid_position(mino):
        return True

    # アクティブミノをNoneに設定
    tetrimino_manager._active_mino = None

    # ゴーストミノを作成 -> Noneが返るはず
    ghost = tetrimino_manager.create_ghost(is_valid_position)

    assert ghost is None
