import unittest
from unittest.mock import patch, MagicMock
import time
from tetris_cli.src.common.singleton import Singleton
from tetris_cli.src.common.trigger import TimeTrigger
from tetris_cli.src.common.key import KeyInput, KeyState, KeyManager
from pynput import keyboard

class TestSingleton(unittest.TestCase):
    def test_singleton(self):
        class MySingleton(Singleton):
            pass
        a = MySingleton()
        b = MySingleton()
        self.assertIs(a, b)

class TestTimeTrigger(unittest.TestCase):
    def test_trigger(self):
        trigger = TimeTrigger(interval=1.0)
        # 強制的に時間を進める
        trigger._last_time = time.time() - 1.1
        self.assertTrue(trigger.is_trigger())
        # リセットされた直後はFalse
        self.assertFalse(trigger.is_trigger())

    def test_reset(self):
        trigger = TimeTrigger(interval=1.0)
        trigger._last_time = 0
        trigger.reset()
        # reset後は現在時刻になるため、すぐにはトリガーされない
        self.assertFalse(trigger.is_trigger())

class TestKeyInput(unittest.TestCase):
    def test_transitions(self):
        k = KeyInput(keyboard.KeyCode.from_char('a'))
        self.assertEqual(k.state, KeyState.HOLD)
        
        # Press
        k.set_pressed(True)
        k.update()
        self.assertEqual(k.state, KeyState.PRESS)
        self.assertEqual(k.elapsed, 0)
        
        # Hold (押しっぱなし)
        k.update()
        self.assertEqual(k.state, KeyState.PRESS)
        self.assertEqual(k.elapsed, 1)
        
        # Release
        k.set_pressed(False)
        k.update()
        self.assertEqual(k.state, KeyState.HOLD)
        self.assertEqual(k.elapsed, 0)

class TestKeyManager(unittest.TestCase):
    def setUp(self):
        # シングルトンのインスタンスをリセット
        if KeyManager in KeyManager._instances:
            del KeyManager._instances[KeyManager]

    @patch('pynput.keyboard.Listener')
    def test_key_manager(self, mock_listener):
        key = keyboard.KeyCode.from_char('a')
        km = KeyManager([key])
        
        # get_key_input
        ki = km.get_key_input(key)
        self.assertIsInstance(ki, KeyInput)
        
        # 無効なキー
        with self.assertRaises(KeyError):
            km.get_key_input(keyboard.KeyCode.from_char('b'))
            
        # コールバック
        km._on_press(key)
        self.assertTrue(ki._is_pressed)
        km._on_release(key)
        self.assertFalse(ki._is_pressed)
        
        # update
        km.update()
        
        # stop
        km.stop()
        km._listener.stop.assert_called_once()
