from enum import Enum


class Color(Enum):
    GRAY: tuple     = (127, 127, 127)
    RED: tuple      = (255, 0, 0)
    GREEN: tuple    = (0, 255, 0)
    BLUE: tuple     = (0, 0, 255)
    YELLOW: tuple   = (255, 255, 0)
    SKYBLUE: tuple  = (0, 255, 255)
    PINK: tuple     = (255, 0, 255)
    ORANGE: tuple   = (255, 165, 0)
