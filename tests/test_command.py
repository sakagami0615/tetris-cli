from tetris_cli.src.tetris.command import (
    RotateCwCommand, RotateCcwCommand, MoveLeftCommand, 
    MoveRightCommand, MoveDownCommand, NoOpTetriminoMoveCommand
)

def test_rotate_cw():
    move = RotateCwCommand().execute()
    assert move.d_rotate == 1

def test_rotate_ccw():
    move = RotateCcwCommand().execute()
    assert move.d_rotate == -1

def test_move_left():
    move = MoveLeftCommand().execute()
    assert move.dc == -1

def test_move_right():
    move = MoveRightCommand().execute()
    assert move.dc == 1

def test_move_down():
    move = MoveDownCommand().execute()
    assert move.dr == 1

def test_noop():
    move = NoOpTetriminoMoveCommand().execute()
    assert move.dr == 0
    assert move.dc == 0
    assert move.d_rotate == 0