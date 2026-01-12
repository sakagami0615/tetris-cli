import sys
from pynput import keyboard

INF = sys.maxsize

HOT_KEY_QUIT = keyboard.KeyCode.from_char("q")
HOT_KEY_MINO_ROTATE_CW = keyboard.Key.up
HOT_KEY_MINO_MOVE_DOWN = keyboard.Key.down
HOT_KEY_MINO_MOVE_RIGHT = keyboard.Key.right
HOT_KEY_MINO_MOVE_LEFT = keyboard.Key.left

HOT_KEY_LIST = [
    HOT_KEY_QUIT,
    HOT_KEY_MINO_ROTATE_CW,
    HOT_KEY_MINO_MOVE_DOWN,
    HOT_KEY_MINO_MOVE_RIGHT,
    HOT_KEY_MINO_MOVE_LEFT,
]

# ボード設定
BOARD_WIDTH = 10
BOARD_HEIGHT = 20

# ゲームループ設定
GAME_LOOP_TRIGGER_TIME = 0.07

# テトリミノの落下速度
TETRIMINO_DROP_INTERVAL = 0.5

# テトリミノの初期位置
TETRIMINO_SPAWN_ROW = 1
TETRIMINO_SPAWN_COL = 5

# キー入力の反復間隔（フレーム数）
KEY_REPEAT_INTERVAL = 2

# 描画の行オフセット（壁を考慮）
RENDER_ROW_OFFSET = 1
