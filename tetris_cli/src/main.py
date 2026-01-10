import keyboard
import random
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

key = None
board = [[0] * WIDTH for _ in range(HEIGHT)]


def key_reset():
    global key
    key = [False] * 5

def key_input():
    if keyboard.is_pressed("q"):
        key[0] = True
    if keyboard.is_pressed("up"):
        key[1] = True
#    if keyboard.is_pressed("down"):
#        key[2] = True
    if keyboard.is_pressed("left"):
        key[3] = True
    if keyboard.is_pressed("right"):
        key[4] = True


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

def display_board():

    for r in range(HEIGHT + 1):
        for c in range(WIDTH + 2):
            if c == 0 or c == WIDTH + 1 or r == HEIGHT:
                console.print_color("■ ", color=Color.GRAY.value, end="")
            elif board[r][c - 1]:
                color = BOARD_COLOR[board[r][c - 1]]
                console.print_color("■ ", color=color, end="")
            else:
                console.print_color("  ", end="")
        console.print_color("")


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
        [( 0,  0), ( 0, -1), ( 1,  0), ( 1,  1)],
        [( 0,  0), (-1,  0), ( 0,  1), ( 1,  1)],
    ],
    # Z mino
    [
        [( 0,  0), ( 0,  1), ( 1, -1), ( 1,  0)],
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



is_continue = True
curr_pos = None
rotate = None
rel_pos_list = None
mino_type = None


def clear_fill_line():
    global board

    is_fill_list = [True] * HEIGHT

    for r in range(HEIGHT):
        for c in range(WIDTH):
            if board[r][c] == 0:
                is_fill_list[r] = False
                break
    
    n_fill_line = sum(is_fill_list)

    board = [line[:] for line, is_fill in zip(board, is_fill_list) if not is_fill]
    board = [[0] * WIDTH for _ in range(n_fill_line)] + board



def put_tetrimino(curr_pos, rel_pos_list):
    global board
    y, x = curr_pos

    for ry, rx in rel_pos_list:
        nx, ny = x + rx, y + ry
        if nx < 0 or nx >= WIDTH or ny >= HEIGHT:
            return False

        if board[ny][nx] != 0:
            return False
    
    for ry, rx in rel_pos_list:
        nx, ny = x + rx, y + ry
        board[ny][nx] = (mino_type + 1)
    return True


def pop_tetrimino(curr_pos, rel_pos_list):
    y, x = curr_pos

    for ry, rx in rel_pos_list:
        nx, ny = x + rx, y + ry
        board[ny][nx] = 0


def spawn_tetrimino():
    global is_continue, curr_pos, rotate, rel_pos_list, mino_type
    curr_pos = [0, 4]
    rotate = 0

    mino_type = random.randrange(len(TETRIMINO))
    rel_pos_list = TETRIMINO[mino_type][rotate][:]

    if not put_tetrimino(curr_pos, rel_pos_list):
        is_continue = False


def move_tetrimino():
    global key, curr_pos, rel_pos_list, rotate, mino_type

    move_pos = curr_pos[:]
    move_rel_pos_list = rel_pos_list[:]
    move_rotate = rotate

    if key[1]:
        move_rotate = (rotate + 1) % len(TETRIMINO[mino_type])
        move_rel_pos_list = TETRIMINO[mino_type][move_rotate][:]
    if key[2]:
        # move_pos[0] += 1
        pass
    if key[3]:
        move_pos[1] -= 1
    if key[4]:
        move_pos[1] += 1
    
    pop_tetrimino(curr_pos, rel_pos_list)
    if not put_tetrimino(move_pos, move_rel_pos_list):
        put_tetrimino(curr_pos, rel_pos_list)
    else:
        curr_pos = move_pos[:]
        rel_pos_list = move_rel_pos_list[:]
        rotate = move_rotate


def down_tetrimino():
    global board, curr_pos, rel_pos_list

    move_pos = curr_pos[:]
    move_pos[0] += 1

    pop_tetrimino(curr_pos, rel_pos_list)
    if not put_tetrimino(move_pos, rel_pos_list):
        put_tetrimino(curr_pos, rel_pos_list)
        curr_pos = None
    else:
        curr_pos = move_pos[:]


def one_step():
    if not curr_pos:
        clear_fill_line()
        spawn_tetrimino()
    else:
        move_tetrimino()
        down_tetrimino()

    display_board()
    console.cursor_up(HEIGHT + 1)


last_time = None

def game_init():
    global last_time
    last_time = time.time()
    key_reset()
    one_step()


def game_end():
    display_board()


def game_loop():
    global key, last_time, is_continue

    while is_continue:
        curr_time = time.time()

        key_input()

        if key[0]:
            break
        
        if curr_time - last_time > 0.1:
            last_time = curr_time
            one_step()
            key_reset()


def main():
    game_init()
    game_loop()
    game_end()
