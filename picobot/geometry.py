from dataclasses import dataclass

AVATAR_SIZE = 42
MARGIN = 4
PADDING = 10
MSG_PADDING_H = 8
MSG_PADDING_V = 6
TIME_PADDING_H = 8
TIME_PADDING_BOTTOM = 6
BOX_HEIGHT = 54
BOX_MIN_WIDTH = 160
BOX_MAX_WIDTH = 264
BOX_RADIUS = 10
FONT_SIZE = 14
LINE_SPACE = 4
LINE_WIDTH_LIMIT = 26
MAX_NUMBER_OF_LINES = 20


@dataclass
class Point:
    x: int
    y: int


@dataclass
class Box:
    top_left: Point
    bottom_right: Point

    def __init__(self, x0, y0, x1, y1):
        self.top_left = Point(x0, y0)
        self.bottom_right = Point(x1, y1)

    def center(self):
        return Point(
            (self.top_left.x + self.bottom_right.x) / 2,
            (self.top_left.y + self.bottom_right.y) / 2,
        )

    def to_list(self):
        return [
            self.top_left.x,
            self.top_left.y,
            self.bottom_right.x,
            self.bottom_right.y,
        ]
