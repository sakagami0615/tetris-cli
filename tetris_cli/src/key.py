import keyboard
from enum import Enum

from tetris_cli.src.common import Singleton
from tetris_cli.src.const import INF
from tetris_cli.src.const import HOT_KEY_LIST


class KeyState(Enum):
    HOLD: int = 0
    PRESS: int = 1


class KeyInput:
    """個別キーの状態を管理"""
    _state: KeyState = KeyState.HOLD
    _elapsed: int = INF
    _key: str

    @property
    def state(self) -> KeyState:
        return self._state

    @property
    def elapsed(self) -> int:
        return self._elapsed

    def __init__(self, key: str):
        self._key = key

    def _transition_to_press(self) -> None:
        """HOLD → PRESS への状態遷移"""
        self._state = KeyState.PRESS
        self._elapsed = 0

    def _transition_to_hold(self) -> None:
        """PRESS → HOLD への状態遷移"""
        self._state = KeyState.HOLD
        self._elapsed = 0

    def update(self) -> None:
        """キー状態を更新"""
        is_pressed = keyboard.is_pressed(self._key)

        if self._state == KeyState.HOLD and is_pressed:
            self._transition_to_press()
        elif self._state == KeyState.PRESS and not is_pressed:
            self._transition_to_hold()
        else:
            self._elapsed += 1


class KeyManager(Singleton):
    _key_input_dict: dict[str, KeyInput]
    _initialized: bool = False

    def __new__(cls):
        instance = super().__new__(cls)
        if not instance._initialized:
            instance._key_input_dict = {hot_key: KeyInput(hot_key) for hot_key in HOT_KEY_LIST}
            instance._initialized = True
        return instance

    def get_key_input(self, hot_key: str) -> KeyInput | None:
        return self._key_input_dict.get(hot_key, None)

    def update(self) -> None:
        for hot_key in HOT_KEY_LIST:
            self._key_input_dict[hot_key].update()