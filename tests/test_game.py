import pytest
from unittest.mock import patch, MagicMock
from tetris_cli.src.tetris.game import Game
from tetris_cli.src.tetris.board import CellType
from tetris_cli.src.tetris.command import MoveRightCommand, MoveLeftCommand, MoveDownCommand, HoldCommand, MoveHardDropCommand
from tetris_cli.src.common.key import KeyState

@pytest.fixture
def game_context():
    # RenderとKeyManager、TimeTriggerをモック化してGameを初期化
    # これにより、テスト中に画面出力やキーボードフックが発生しないようにする
    patchers = [
        patch('tetris_cli.src.tetris.game.Render'),
        patch('tetris_cli.src.tetris.game.KeyManager'),
        patch('tetris_cli.src.tetris.game.TimeTrigger'),
    ]
    
    mocks = [patcher.start() for patcher in patchers]
    game = Game()
    
    yield game, mocks

    for patcher in patchers:
        patcher.stop()

def test_initial_state(game_context):
    """ゲーム初期状態の確認"""
    game, _ = game_context
    assert game.is_continue
    assert game.active_mino is not None
    assert game.score == 0
    assert game.can_hold

def test_apply_command_move(game_context):
    """移動コマンドの適用テスト"""
    game, _ = game_context
    # 初期位置を取得
    initial_c = game.active_mino.c
    initial_r = game.active_mino.r

    # 右移動
    game._apply_command(MoveRightCommand())
    assert game.active_mino.c == initial_c + 1

    # 左移動（元の位置に戻る）
    game._apply_command(MoveLeftCommand())
    assert game.active_mino.c == initial_c

    # 下移動
    game._apply_command(MoveDownCommand())
    assert game.active_mino.r == initial_r + 1

def test_collision_detection(game_context):
    """衝突判定のテスト"""
    game, _ = game_context
    # 壁にぶつかるまで右に移動させる
    # ボード幅は10なので十分な回数移動
    cmd = MoveRightCommand()
    for _ in range(20):
        game._apply_command(cmd)
    
    # 最終的な位置が有効であることを確認（壁の中にめり込んでいないか）
    assert game._is_valid_position(game.active_mino)
    
    # さらに右に行こうとしても座標が変わらないことを確認
    last_c = game.active_mino.c
    game._apply_command(cmd)
    assert game.active_mino.c == last_c

def test_hold(game_context):
    """ホールド機能のテスト"""
    game, _ = game_context
    # 初回ホールド
    first_mino_type = game.active_mino.mino_type
    game._execute_hold()
    
    assert game.hold_mino is not None
    assert game.hold_mino.mino_type == first_mino_type
    assert not game.can_hold
    
    # 連続ホールドは不可
    current_mino_type = game.active_mino.mino_type
    game._execute_hold()
    # 変わっていないはず
    assert game.active_mino.mino_type == current_mino_type

def test_hard_drop(game_context):
    """ハードドロップのテスト"""
    game, _ = game_context
    initial_r = game.active_mino.r
    game._execute_hard_drop()
    
    # 新しいミノがスポーンしているはず（位置が初期位置に戻っている、または別のミノになっている）
    # 少なくとも元の位置よりは下に落ちて固定されているはずだが、
    # _execute_hard_drop内で_spawn_tetriminoが呼ばれるため、active_minoは新品になる
    assert game.active_mino.r == 1 # TETRIMINO_SPAWN_ROW

def test_ghost_mino(game_context):
    """ゴーストミノ作成のテスト"""
    game, _ = game_context
    ghost = game._create_ghost_mino()
    assert ghost is not None
    # ゴーストはアクティブミノと同じかそれより下にいるはず
    assert ghost.r >= game.active_mino.r

def test_game_over(game_context):
    """ゲームオーバー判定のテスト"""
    game, _ = game_context
    # スポーン位置を埋める
    game.board.cells[1][5].cell_type = CellType.MINO
    
    game._spawn_tetrimino()
    assert not game.is_continue

def test_get_input_commands(game_context):
    """入力コマンド取得のテスト"""
    game, mocks = game_context
    # KeyManagerのモックを取得
    mock_km_cls = mocks[1]
    mock_km_instance = mock_km_cls.return_value
    
    # 特定のキー入力をシミュレート
    mock_key_input = MagicMock()
    mock_key_input.state = KeyState.PRESS
    mock_key_input.elapsed = 0
    
    # どのキーを要求されてもPRESS状態を返すように設定
    mock_km_instance.get_key_input.return_value = mock_key_input
    
    # TimeTriggerもTrueにする
    game.down_mino_trigger.is_trigger = MagicMock(return_value=True)
    
    commands = game._get_input_commands()
    
    # 複数のコマンドが生成されるはず
    assert len(commands) > 0
    # HoldCommandが含まれているか確認
    assert any(isinstance(c, HoldCommand) for c in commands)


def test_apply_commands_priority(game_context):
    """コマンド適用の優先順位テスト（特殊コマンド優先）"""
    game, _ = game_context
    
    # 特殊コマンド（Hold）と通常コマンド（MoveRight）を同時に渡す
    # Holdが実行されれば can_hold が False になる
    # MoveRight は無視されるはず（位置が変わらない、またはHold後の初期位置になる）
    commands = [MoveRightCommand(), HoldCommand()]
    
    game._apply_commands(commands)
    
    assert not game.can_hold
    # Hold実行後は新しいミノがスポーンするため、初期位置(5)にいるはず
    assert game.active_mino.c == 5

def test_apply_commands_separation(game_context):
    """コマンド適用の順序テスト（回転・横移動 -> 下移動）"""
    game, _ = game_context
    
    # 右移動と下移動を渡す
    # 内部で分離されて処理される（横移動が先、下移動が後）
    initial_r = game.active_mino.r
    initial_c = game.active_mino.c
    
    commands = [MoveDownCommand(), MoveRightCommand()]
    game._apply_commands(commands)
    
    assert game.active_mino.c == initial_c + 1
    assert game.active_mino.r == initial_r + 1

def test_update_and_draw(game_context):
    """updateとdrawメソッドの呼び出しテスト"""
    game, mocks = game_context
    # mocks[0] is Render patcher
    mock_render_instance = mocks[0].return_value
    
    # update
    with patch.object(game, '_get_input_commands', return_value=[]):
        game.update()
        
    # draw
    game.draw()
    assert mock_render_instance.draw.called

def test_hold_game_over(game_context):
    """ホールド時のスポーンでゲームオーバーになるケース"""
    game, _ = game_context
    
    # スポーン位置を埋める
    game.board.cells[1][5].cell_type = CellType.MINO
    
    # ホールド実行（初回） -> 新しいミノをスポーンしようとして衝突 -> ゲームオーバー
    game._execute_hold()
    
    assert not game.is_continue