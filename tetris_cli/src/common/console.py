import sys
import platform


def print_color(msg, color=(255, 255, 255), end=None):
    """カラー出力（coloramaでクロスプラットフォーム対応）"""
    r, g, b = color
    print(f"\033[38;2;{r};{g};{b}m{msg}", end=end)


def cursor_up(n):
    """カーソルを上に移動（coloramaでクロスプラットフォーム対応）"""
    print(f"\033[{n}A", end="")


def clear_input_buffer() -> None:
    """入力バッファをクリア"""
    if platform.system() == 'Windows':
        try:
            import msvcrt
            while msvcrt.kbhit():
                msvcrt.getch()
        except ImportError:
            pass
    else:
        import termios
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)


def disable_echo():
    """ターミナルのエコーを無効化（キー入力を画面に表示しない）"""
    if platform.system() == 'Windows':
        try:
            import msvcrt
            # Windowsではコンソールモードを変更
            import ctypes
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-10)  # STD_INPUT_HANDLE
            mode = ctypes.c_ulong()
            kernel32.GetConsoleMode(handle, ctypes.byref(mode))
            # ENABLE_ECHO_INPUT (0x0004) を無効化
            new_mode = mode.value & ~0x0004
            kernel32.SetConsoleMode(handle, new_mode)
            return mode.value
        except Exception:
            return None
    else:
        import tty
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        new_settings = termios.tcgetattr(fd)
        # ECHO フラグを無効化
        new_settings[3] = new_settings[3] & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSADRAIN, new_settings)
        return old_settings


def restore_echo(old_settings):
    """ターミナルのエコーを元に戻す"""
    if old_settings is None:
        return

    if platform.system() == 'Windows':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-10)
            kernel32.SetConsoleMode(handle, old_settings)
        except Exception:
            pass
    else:
        import termios
        fd = sys.stdin.fileno()
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
