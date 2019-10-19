from enum import IntEnum


class MsgType(IntEnum):
    TEXT = 1
    PHOTO = 2
    DOCUMENT = 3
    STICKER = 4
    REP_TEXT = 10
    REP_PHOTO = 20
    REP_DOCUMENT = 30
    REP_STICKER = 40
