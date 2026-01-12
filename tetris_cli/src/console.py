import sys
import platform


def print_color(msg, color=(255, 255, 255), end=None):
    r, g, b = color
    print(f"\033[38;2;{r};{g};{b}m{msg}", end=end)


def cursor_up(n):
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
