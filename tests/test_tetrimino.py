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

def test_next_mino(tetrimino_manager):
    """次に出現するミノのプレビューテスト"""
    # next_minoプロパティが正しく動作することを確認
    next_mino = tetrimino_manager.next_mino

    assert next_mino is not None
    assert isinstance(next_mino, Tetrimino)
    assert next_mino.r == 1  # 初期位置
    assert next_mino.c == 5  # 初期位置

    # 次のミノを取得しても spawner の状態が変わらないことを確認
    next_mino_again = tetrimino_manager.next_mino
    assert next_mino_again.mino_type == next_mino.mino_type

    # アクティブミノをスポーンさせて、次のミノが正しく更新されることを確認
    def is_valid_position(mino):
        return True

    original_next_type = next_mino.mino_type
    tetrimino_manager.spawn(is_valid_position)

    # スポーン後のアクティブミノは元のnext_minoと同じタイプのはず
    assert tetrimino_manager.active_mino.mino_type == original_next_type

def test_next_minos(tetrimino_manager):
    """次に出現する複数のミノのプレビューテスト"""
    # next_minosプロパティが正しく動作することを確認
    next_minos = tetrimino_manager.next_minos

    assert len(next_minos) == 3
    for next_mino in next_minos:
        assert isinstance(next_mino, Tetrimino)
        assert next_mino.r == 1  # 初期位置
        assert next_mino.c == 5  # 初期位置

    # 次のミノを取得しても spawner の状態が変わらないことを確認
    next_minos_again = tetrimino_manager.next_minos
    for i in range(3):
        assert next_minos_again[i].mino_type == next_minos[i].mino_type

    # アクティブミノをスポーンさせて、次のミノが正しく更新されることを確認
    def is_valid_position(mino):
        return True

    original_first_type = next_minos[0].mino_type
    tetrimino_manager.spawn(is_valid_position)

    # スポーン後のアクティブミノは元のnext_minos[0]と同じタイプのはず
    assert tetrimino_manager.active_mino.mino_type == original_first_type

    # next_minosの先頭は元の2番目がスライドしているはず
    new_next_minos = tetrimino_manager.next_minos
    assert new_next_minos[0].mino_type == next_minos[1].mino_type
