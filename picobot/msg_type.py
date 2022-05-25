from enum import IntEnum


class MsgType(IntEnum):
    TEXT = 1
    PHOTO = 2
    DOCUMENT = 3
    DOCUMENT_VIDEO = 4
    STICKER = 5
    VIDEO = 6
    VIDEO_NOTE = 7
    VIDEO_STICKER = 8
    REP_TEXT = 10
    REP_PHOTO = 20
    REP_DOCUMENT = 30
    REP_DOCUMENT_VIDEO = 40
    REP_STICKER = 50
    REP_VIDEO = 60
    REP_VIDEO_NOTE = 70
    REP_VIDEO_STICKER = 80
