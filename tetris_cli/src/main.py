import keyboard
import random
import sys
import time
from enum import Enum

from tetris_cli.src import console


class Color(Enum):
    GRAY: tuple     = (127, 127, 127)
    RED: tuple      = (255, 0, 0)
    GREEN: tuple    = (0, 255, 0)
    BLUE: tuple     = (0, 0, 255)
    YELLOW: tuple   = (255, 255, 0)
    SKYBLUE: tuple  = (0, 255, 255)
    PINK: tuple     = (255, 0, 255)
    ORANGE: tuple   = (255, 165, 0)


WIDTH = 10
HEIGHT = 20
FPS = 60


INF = sys.maxsize



class TimeTrigger:
    _last_unix_time: float = time.time()
    _unix_time_interval: float

    def __init__(self, unix_time_interval: float):
        self._unix_time_interval = unix_time_interval

    def is_trigger(self) -> bool:
        curr_unix_time: float = time.time()
        if curr_unix_time - self._last_unix_time >= self._unix_time_interval:
            self._last_unix_time = curr_unix_time
            return True
        else:
            return False


class KeyState(Enum):
    HOLD: int = 0
    PRESS: int = 1


class KeyInput:
    _state: KeyState = KeyState.HOLD
    _elapsed: int = INF
    _key: str

    @property
    def state(self):
        return self._state
    
    @property
    def elapsed(self):
        return self._elapsed

    def __init__(self, key: str):
        self._key = key
    
    def update(self):
        is_pressed = keyboard.is_pressed(self._key)
        
        if (self._state == KeyState.HOLD) and is_pressed:
            self._state = KeyState.PRESS
            self._elapsed = 0
        elif (self._state == KeyState.PRESS) and (not is_pressed):
            self._state = KeyState.HOLD
            self._elapsed = 0
        else:
            self._elapsed += 1


HOT_KEY_Q = "q"
HOT_KEY_UP = "up"
HOT_KEY_DOWN = "down"
HOT_KEY_RIGHT = "right"
HOT_KEY_LEFT = "left"

HOT_KEY_LIST = [
    HOT_KEY_Q,
    HOT_KEY_UP,
    HOT_KEY_DOWN,
    HOT_KEY_RIGHT,
    HOT_KEY_LEFT,
]


class Keyboard:
    
    _key_input_dict: dict[str, KeyInput]

    def __init__(self):
        self._key_input_dict = {hot_key: KeyInput(hot_key) for hot_key in HOT_KEY_LIST} 
        
    def get_key_input(self, hot_key: str) -> KeyInput | None:
        return self._key_input_dict.get(hot_key, None)

    def update(self) -> None:
        for hot_key in HOT_KEY_LIST:
            self._key_input_dict[hot_key].update()


key_manager = Keyboard()


BOARD_COLOR = [
    None,
    Color.YELLOW.value,
    Color.SKYBLUE.value,
    Color.ORANGE.value,
    Color.BLUE.value,
    Color.GREEN.value,
    Color.RED.value,
    Color.PINK.value,
]


TETRIMINO = [
    # O mino
    [
        [( 0,  0), ( 1,  0), ( 1,  1), ( 0,  1)],
    ],
    # I mino
    [
        [( 0,  0), ( 0, -1), ( 0,  1), ( 0,  2)],
        [( 0,  0), (-1,  0), ( 1,  0), ( 2,  0)],
    ],
    # L mino
    [
        [( 0,  0), ( 0, -1), ( 0,  1), ( 1,  1)],
        [( 0,  0), (-1,  0), ( 1,  0), ( 1, -1)],
        [( 0,  0), (-1, -1), ( 0, -1), ( 0,  1)],
        [( 0,  0), (-1,  0), ( 1,  0), (-1,  1)],
    ],
    # J mino
    [
        [( 0,  0), ( 0, -1), ( 0,  1), ( 1, -1)],
        [( 0,  0), (-1,  0), (-1, -1), ( 1,  0)],
        [( 0,  0), (-1,  1), ( 0, -1), ( 0,  1)],
        [( 0,  0), (-1,  0), ( 1,  0), ( 1,  1)],
    ],
    # S mino
    [
        [( 0,  0), ( 0,  1), ( 1, -1), ( 1,  0)],
        [( 0,  0), (-1,  0), ( 0,  1), ( 1,  1)],
    ],
    # Z mino
    [
        [( 0,  0), ( 0, -1), ( 1,  0), ( 1,  1)],
        [( 0,  0), (-1,  1), ( 0,  1), ( 1,  0)],
    ],
    # T mino
    [
        [( 0,  0), ( 0, -1), ( 0,  1), ( 1,  0)],
        [( 0,  0), (-1,  0), ( 0, -1), ( 1,  0)],
        [( 0,  0), (-1,  0), ( 0, -1), ( 0,  1)],
        [( 0,  0), (-1,  0), ( 0,  1), ( 1,  0)],
    ],
]


class Game:

    _is_continue: bool = True
    _down_mino_trigger: TimeTrigger = TimeTrigger(0.1)

    _board = [[0] * WIDTH for _ in range(HEIGHT)]

    _curr_pos: list[int] = None
    _rotate: int = None
    _rel_pos_list: list[list[tuple[int, int]]] = None
    _mino_type: int = None

    @property
    def is_continue(self):
        return self._is_continue

    def display_board(self):
        for r in range(HEIGHT + 1):
            for c in range(WIDTH + 2):
                if c == 0 or c == WIDTH + 1 or r == HEIGHT:
                    console.print_color("■ ", color=Color.GRAY.value, end="")
                elif self._board[r][c - 1]:
                    color = BOARD_COLOR[self._board[r][c - 1]]
                    console.print_color("■ ", color=color, end="")
                else:
                    console.print_color("  ", end="")
            console.print_color("")

    def clear_fill_line(self):
        is_fill_list = [True] * HEIGHT

        for r in range(HEIGHT):
            for c in range(WIDTH):
                if self._board[r][c] == 0:
                    is_fill_list[r] = False
                    break
        
        n_fill_line = sum(is_fill_list)

        self._board = [line[:] for line, is_fill in zip(self._board, is_fill_list) if not is_fill]
        self._board = [[0] * WIDTH for _ in range(n_fill_line)] + self._board

    def put_tetrimino(self, curr_pos, rel_pos_list):
        y, x = curr_pos

        for ry, rx in rel_pos_list:
            nx, ny = x + rx, y + ry
            if nx < 0 or nx >= WIDTH or ny >= HEIGHT:
                return False

            if self._board[ny][nx] != 0:
                return False
        
        for ry, rx in rel_pos_list:
            nx, ny = x + rx, y + ry
            self._board[ny][nx] = (self._mino_type + 1)
        return True


    def pop_tetrimino(self, curr_pos, rel_pos_list):
        y, x = curr_pos

        for ry, rx in rel_pos_list:
            nx, ny = x + rx, y + ry
            self._board[ny][nx] = 0


    def spawn_tetrimino(self):
        self._curr_pos = [0, 4]
        self._rotate = 0

        self._mino_type = random.randrange(len(TETRIMINO))
        self._rel_pos_list = TETRIMINO[self._mino_type][self._rotate][:]

        if not self.put_tetrimino(self._curr_pos, self._rel_pos_list):
            self._is_continue = False


    def move_tetrimino(self):
        move_pos = self._curr_pos[:]
        move_rel_pos_list = self._rel_pos_list[:]
        move_rotate = self._rotate

        key_up = key_manager.get_key_input(HOT_KEY_UP)
        key_down = key_manager.get_key_input(HOT_KEY_DOWN)
        key_left = key_manager.get_key_input(HOT_KEY_LEFT)
        key_right = key_manager.get_key_input(HOT_KEY_RIGHT)

        is_down = False
        if (key_up.state == KeyState.PRESS) and (key_up.elapsed % 2 == 0):
            move_rotate = (move_rotate + 1) % len(TETRIMINO[self._mino_type])
            move_rel_pos_list = TETRIMINO[self._mino_type][move_rotate][:]
        if (key_down.state == KeyState.PRESS) and (key_down.elapsed % 2 == 0):
            # move_pos[0] += 1
            is_down = True
        if (key_left.state == KeyState.PRESS) and (key_left.elapsed % 2 == 0):
            move_pos[1] -= 1
        if (key_right.state == KeyState.PRESS) and (key_right.elapsed % 2 == 0):
            move_pos[1] += 1
        
        self.pop_tetrimino(self._curr_pos, self._rel_pos_list)
        if not self.put_tetrimino(move_pos, move_rel_pos_list):
            self.put_tetrimino(self._curr_pos, self._rel_pos_list)
        else:
            self._curr_pos = move_pos[:]
            self._rel_pos_list = move_rel_pos_list[:]
            self._rotate = move_rotate
        
        return is_down


    def down_tetrimino(self):
        move_pos = self._curr_pos[:]
        move_pos[0] += 1

        self.pop_tetrimino(self._curr_pos, self._rel_pos_list)
        if not self.put_tetrimino(move_pos, self._rel_pos_list):
            self.put_tetrimino(self._curr_pos, self._rel_pos_list)
            self._curr_pos = None
        else:
            self._curr_pos = move_pos[:]


    def update(self):
        if not self._curr_pos:
            self.clear_fill_line()
            self.spawn_tetrimino()
        else:
            is_down = self.move_tetrimino()
            if is_down or self._down_mino_trigger.is_trigger():
                self.down_tetrimino()

        self.display_board()
        console.cursor_up(HEIGHT + 1)


class GameManager:

    _game = Game()
    _game_loop_trigger: TimeTrigger = TimeTrigger(0.1)

    _is_continue: bool = True


    def __init__(self):
        self._game.display_board()
        console.cursor_up(HEIGHT + 1)

    def __del__(self):
        self._game.display_board()
    
    def game_loop(self) -> None:
        global is_continue

        while self._game.is_continue:
            
            if self._game_loop_trigger.is_trigger():            
                self._game.update()
                key_manager.update()
            
            if key_manager.get_key_input(HOT_KEY_Q).state == KeyState.PRESS:
                break


def main():
    game_manager = GameManager()
    game_manager.game_loop()
    