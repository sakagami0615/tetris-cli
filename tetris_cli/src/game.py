
from tetris_cli.src.board import Board
from tetris_cli.src.key import KeyManager, KeyState
from tetris_cli.src.trigger import TimeTrigger
from tetris_cli.src.tetrimino import ActiveTetrimino
from tetris_cli.src.ui import Render
from tetris_cli.src.const import HOT_KEY_QUIT, HOT_KEY_MINO_ROTATE_CW, HOT_KEY_MINO_MOVE_DOWN, HOT_KEY_MINO_MOVE_RIGHT, HOT_KEY_MINO_MOVE_LEFT
from tetris_cli.src.const import GAME_LOOP_TRIGGER_TIME


class Game:
    is_continue: bool = True
    down_mino_trigger: TimeTrigger = TimeTrigger(0.5)

    render: Render
    board: Board
    active_mino: ActiveTetrimino | None


    def __init__(self):        
        self.render = Render()
        self.board = Board()
        self.active_mino = ActiveTetrimino(1, 5)

    def _control_tetrimino_rotate(self) -> int:
        rotate, n_rotate = self.active_mino.rotate, self.active_mino.n_rotate

        key_rot_cw = KeyManager().get_key_input(HOT_KEY_MINO_ROTATE_CW)
        if (key_rot_cw.state == KeyState.PRESS) and (key_rot_cw.elapsed % 2 == 0):
            rotate = (rotate + 1) % n_rotate
        return rotate

    def _control_tetrimino_horizontally(self) -> int:
        c = self.active_mino.c
        
        key_move_left = KeyManager().get_key_input(HOT_KEY_MINO_MOVE_LEFT)
        key_move_right = KeyManager().get_key_input(HOT_KEY_MINO_MOVE_RIGHT)
        if (key_move_left.state == KeyState.PRESS) and (key_move_left.elapsed % 2 == 0):
            c -= 1
        if (key_move_right.state == KeyState.PRESS) and (key_move_right.elapsed % 2 == 0):
            c += 1
        return c

    def _control_tetrimino_down(self) -> int:
        r = self.active_mino.r
        
        key_move_down = KeyManager().get_key_input(HOT_KEY_MINO_MOVE_DOWN)
        if (self.down_mino_trigger.is_trigger() or 
           (key_move_down.state == KeyState.PRESS) and (key_move_down.elapsed % 2 == 0)):
            r += 1
        return r

    def _check_put_tetrimino(self, mino: ActiveTetrimino):
        for r, c in mino.blocks():
            cell = self.board.cells[r][c]
            if cell.fill:
                return False
        return True

    def _spawn_tetrimino(self):
        self.active_mino.spawn(1, 5)
        if not self._check_put_tetrimino(self.active_mino):
            self.active_mino = None
            self.is_continue = False

    def update(self):
        r, c, rotate = self.active_mino.r, self.active_mino.c, self.active_mino.rotate
        next_rotate = self._control_tetrimino_rotate()
        next_c = self._control_tetrimino_horizontally()
        next_r = self._control_tetrimino_down()

        self.active_mino.c = next_c
        self.active_mino.r = next_r
        self.active_mino.rotate = next_rotate

        if not self._check_put_tetrimino(self.active_mino):
            self.active_mino.c = c
            self.active_mino.r = r
            self.active_mino.rotate = rotate
            
            if next_r != r:
                self.board.write_tetrimino(self.active_mino)
                self.board.clear_fill_lines()
                self._spawn_tetrimino()

    def draw(self, is_cursor_up: bool = True):
        self.render.draw(self.board, self.active_mino, is_cursor_up)


class GameManager:
    game: Game
    game_loop_trigger: TimeTrigger

    def __init__(self):
        self.game = Game()
        self.game_loop_trigger: TimeTrigger = TimeTrigger(GAME_LOOP_TRIGGER_TIME)


    def __del__(self):
        self.game.draw(is_cursor_up=False)

    def game_loop(self) -> None:
        while self.game.is_continue:
            
            if self.game_loop_trigger.is_trigger():            
                self.game.update()
                self.game.draw()
                KeyManager().update()
            
            if KeyManager().get_key_input(HOT_KEY_QUIT).state == KeyState.PRESS:
                break
