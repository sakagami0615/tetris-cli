from enum import Enum
from typing import TypeAlias
from pynput import keyboard

from tetris_cli.src.common import Singleton
from tetris_cli.src.const import INF
from tetris_cli.src.const import HOT_KEY_LIST

# 型エイリアス
KeyType: TypeAlias = keyboard.Key | keyboard.KeyCode


class KeyState(Enum):
    HOLD: int = 0
    PRESS: int = 1


class KeyInput:
    """個別キーの状態を管理"""
    _state: KeyState = KeyState.HOLD
    _elapsed: int = INF
    _key: KeyType
    _is_pressed: bool = False

    @property
    def state(self) -> KeyState:
        return self._state

    @property
    def elapsed(self) -> int:
        return self._elapsed

    def __init__(self, key: KeyType):
        self._key = key

    def _transition_to_press(self) -> None:
        """HOLD → PRESS への状態遷移"""
        self._state = KeyState.PRESS
        self._elapsed = 0

    def _transition_to_hold(self) -> None:
        """PRESS → HOLD への状態遷移"""
        self._state = KeyState.HOLD
        self._elapsed = 0

    def set_pressed(self, pressed: bool) -> None:
        """キーが押されているかを設定"""
        self._is_pressed = pressed

    def update(self) -> None:
        """キー状態を更新"""
        if self._state == KeyState.HOLD and self._is_pressed:
            self._transition_to_press()
        elif self._state == KeyState.PRESS and not self._is_pressed:
            self._transition_to_hold()
        else:
            self._elapsed += 1


class KeyManager(Singleton):
    """キー入力を管理するシングルトンクラス"""
    _key_input_dict: dict[KeyType, KeyInput]
    _listener: keyboard.Listener
    _initialized: bool = False

    def __new__(cls):
        instance = super().__new__(cls)
        if not instance._initialized:
            instance._key_input_dict = {hot_key: KeyInput(hot_key) for hot_key in HOT_KEY_LIST}
            instance._listener = keyboard.Listener(
                on_press=instance._on_press,
                on_release=instance._on_release
            )
            instance._listener.start()
            instance._initialized = True
        return instance

    def _on_press(self, key: KeyType) -> None:
        """キーが押されたときのコールバック"""
        if key in self._key_input_dict:
            self._key_input_dict[key].set_pressed(True)

    def _on_release(self, key: KeyType) -> None:
        """キーが離されたときのコールバック"""
        if key in self._key_input_dict:
            self._key_input_dict[key].set_pressed(False)

    def get_key_input(self, hot_key: KeyType) -> KeyInput | None:
        """指定されたキーの入力状態を取得"""
        return self._key_input_dict.get(hot_key, None)

    def update(self) -> None:
        """全てのキー入力を更新"""
        for hot_key in HOT_KEY_LIST:
            self._key_input_dict[hot_key].update()

    def stop(self) -> None:
        """キーリスナーを停止"""
        if hasattr(self, '_listener'):
            self._listener.stop()