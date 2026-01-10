def print_color(msg, color=(255, 255, 255), end=None):
    r, g, b = color
    print(f"\033[38;2;{r};{g};{b}m{msg}", end=end)


def cursor_up(n):
    print(f"\033[{n}A", end="")
