from typing import Tuple
from PIL import Image, ImageDraw, ImageFont
from emoji import emoji_lis, emoji_count

from .config import ROOT_DIR
from .geometry import (
    AVATAR_SIZE,
    MARGIN,
    PADDING,
    MSG_PADDING_H,
    MSG_PADDING_V,
    TIME_PADDING_H,
    TIME_PADDING_BOTTOM,
    BOX_MIN_WIDTH,
    BOX_RADIUS,
    FONT_SIZE,
    LINE_SPACE,
    Point,
    Box,
)

IMG_DIR = ROOT_DIR / 'images'
FONT_DIR = ROOT_DIR / 'fonts'
IMG_PREFIX = 'img'
AVATAR_MASK_NAME = 'avatar_mask.png'

BOX_COLOR = "#182533"
TITLE_COLOR = "#338cf3"
TEXT_COLOR = "#dddddd"
TIME_COLOR = "#6A7B8C"
EMOJI_JOINER = chr(0xFE0F)


def draw_balloon(img_draw: ImageDraw.Draw, points: Box, fill=None, width=0):
    r_x0 = points.top_left.x
    r_y0 = points.top_left.y + BOX_RADIUS
    r_x1 = points.bottom_right.x
    r_y1 = points.bottom_right.y - BOX_RADIUS
    img_draw.rectangle([r_x0, r_y0, r_x1, r_y1], fill=fill, width=width)
    r_x0 = points.top_left.x + BOX_RADIUS
    r_y0 = points.top_left.y
    r_x1 = points.bottom_right.x - BOX_RADIUS
    r_y1 = points.bottom_right.y
    img_draw.rectangle([r_x0, r_y0, r_x1, r_y1], fill=fill, width=width)
    diam = 2 * BOX_RADIUS
    c_x0 = points.top_left.x
    c_y0 = points.top_left.y
    c_x1 = c_x0 + diam
    c_y1 = c_y0 + diam
    img_draw.ellipse([c_x0, c_y0, c_x1, c_y1], fill=fill, width=width)
    c_x0 = points.bottom_right.x - diam
    c_x1 = c_x0 + diam
    img_draw.ellipse([c_x0, c_y0, c_x1, c_y1], fill=fill, width=width)
    c_y0 = points.bottom_right.y - diam
    c_y1 = c_y0 + diam
    img_draw.ellipse([c_x0, c_y0, c_x1, c_y1], fill=fill, width=width)

    arrow_x = 10
    arrow_y = 10 if BOX_RADIUS < 10 else BOX_RADIUS
    arrow = [
        (points.top_left.x - arrow_x, points.bottom_right.y),
        (points.top_left.x, points.bottom_right.y - arrow_y),
        (points.top_left.x + diam, points.bottom_right.y - arrow_y),
        (points.top_left.x + diam, points.bottom_right.y),
    ]
    img_draw.polygon(arrow, fill=fill)


def draw_username(
    txt_draw: ImageDraw.ImageDraw,
    position: Point,
    username="Jojo",
    fill=TITLE_COLOR,
    font=None,
):
    x0 = position.x + MSG_PADDING_H
    y0 = position.y + MSG_PADDING_V
    txt_draw.text((x0, y0), username, font=font, fill=fill)


def draw_message(
    txt_draw: ImageDraw.ImageDraw,
    points: Box,
    text="Oi, eu sou o Jojo",
    fill=TEXT_COLOR,
    font=None,
    user_size=[0, 0],
):
    current_position = Point(
        points.top_left.x + MSG_PADDING_H,
        points.top_left.y + MSG_PADDING_V + user_size[1] + LINE_SPACE,
    )
    symbola_font = ImageFont.truetype(font=str(FONT_DIR / 'Symbola.ttf'), size=16)
    emoji_locations = emoji_lis(text)
    indexes = [0]

    # Some complex emojis use \u200d as a zero-width character to join two emojis into one
    # Pillow doesn't work with this and use chr(0xFE0F) instead
    text = text.replace('\u200d', EMOJI_JOINER)

    def draw_emoji(em: dict):
        current_text = em['emoji']
        txt_draw.text(
            (current_position.x, current_position.y + 4),
            text=em['emoji'],
            font=symbola_font,
            fill=TEXT_COLOR,
        )
        incr = 1
        if len(text) > em['location'] + 1 and text[em['location'] + 1] == EMOJI_JOINER:
            incr = 2
        indexes.append(em['location'] + incr)
        current_position.x += txt_draw.textsize(current_text, font=symbola_font)[0]

    def draw_text(text: str):
        lines = text.split('\n')
        for line in lines[:-1]:
            txt_draw.text(
                current_position.to_tuple(), text=line, font=font, fill=TEXT_COLOR
            )
            textsize = txt_draw.textsize(' ', font=font)
            current_position.x = points.top_left.x + MSG_PADDING_H
            current_position.y += textsize[1] + LINE_SPACE
        text = lines[-1]
        txt_draw.text(
            current_position.to_tuple(), text=text, font=font, fill=TEXT_COLOR
        )
        displacement = txt_draw.textsize(text, font=font)
        current_position.x += displacement[0]

    for em in emoji_locations:
        last_index = indexes[-1]
        if em['location'] - 1 < last_index:  # last drawn symbol was an emoji
            draw_emoji(em)
        else:
            current_text = text[last_index : em['location']]
            draw_text(current_text)
            draw_emoji(em)
    if indexes[-1] < len(text):
        current_text = text[indexes[-1] :]
        draw_text(current_text)


def draw_time(
    txt_draw: ImageDraw.ImageDraw, points: Box, text="04:20", fill=TEXT_COLOR, font=None
):
    tw = txt_draw.textsize(text, font=font)
    x0 = points.bottom_right.x - TIME_PADDING_H - tw[0]
    y0 = points.bottom_right.y - (TIME_PADDING_BOTTOM + tw[1])
    txt_draw.text((x0, y0), text, font=font, fill=TIME_COLOR)


def draw_avatar(
    img: Image,
    draw: ImageDraw.ImageDraw,
    username: str,
    points_balloon: Box,
    avatar_path: str,
):
    y0 = points_balloon.bottom_right.y - AVATAR_SIZE
    y1 = points_balloon.bottom_right.y
    points = Box(MARGIN, y0, MARGIN + AVATAR_SIZE, y1)
    box_position = tuple(a - 2 for a in points.top_left.to_tuple())
    size = AVATAR_SIZE + 4
    if avatar_path == '':
        draw.ellipse(points.to_list(), fill=TITLE_COLOR)
        avatar_font = ImageFont.truetype(
            font=str(FONT_DIR / 'OpenSans-SemiBold.ttf'), size=20
        )
        avatar_center = points.center().to_tuple()
        draw.text(
            avatar_center, username[0], anchor='mm', font=avatar_font, fill='#FFFFFF'
        )
        return

    avatar = Image.open(avatar_path).convert(mode='RGBA')
    if avatar.width == avatar.height:
        avatar = avatar.resize((size, size), resample=Image.ANTIALIAS)
    elif avatar.width > avatar.height:
        ratio = size / avatar.width
        avatar = avatar.resize(
            (size, int(ratio * avatar.height)), resample=Image.ANTIALIAS
        )
    else:
        ratio = size / avatar.height
        avatar = avatar.resize(
            (int(ratio * avatar.width), size), resample=Image.ANTIALIAS
        )

    avatar_mask = generate_avatar_mask(img.size, points)
    tmp = Image.new('RGBA', img.size)
    tmp.paste(avatar, box=box_position)
    img.paste(tmp, mask=avatar_mask)


def sticker_from_text(
    user_id: int, username: str, text: str, avatar_path: str, msg_time: str
):
    size = (512, 256)
    transparent = (0, 0, 0, 0)

    bold_font = ImageFont.truetype(
        font=str(FONT_DIR / 'OpenSans-Bold.ttf'), size=FONT_SIZE
    )
    font = ImageFont.truetype(
        font=str(FONT_DIR / 'OpenSans-SemiBold.ttf'), size=FONT_SIZE
    )
    time_font = ImageFont.truetype(font=str(FONT_DIR / 'OpenSans-Regular.ttf'), size=13)

    username = username if (len(username) < 26) else f'{username[0:25]}...'
    limit_is_user = len(username) >= len(text)
    aux_img = ImageDraw.Draw(Image.new('RGBA', size, transparent))
    title_size = aux_img.textsize(username, font=bold_font)
    text_size = aux_img.textsize(text, font=font)
    additional_space_for_emojis = 5 * emoji_count(text)
    text_size = (text_size[0] + additional_space_for_emojis, text_size[1])
    time_size = aux_img.textsize('04:20', font=time_font)
    final_text = text

    if limit_is_user:
        bigger_size = title_size
    else:
        if len(text) >= 26:
            aux_text = wrapped_text(text, line_limit=26)
            text_size = aux_img.multiline_textsize(aux_text, font=font)
            final_text = aux_text
        bigger_size = text_size
    box_size = (
        bigger_size[0] + 2 * MSG_PADDING_H,
        title_size[1]
        + bigger_size[1]
        + 2 * MSG_PADDING_V
        + time_size[1]
        + 2 * LINE_SPACE,
    )

    b_width = max(BOX_MIN_WIDTH, box_size[0])
    b_height = box_size[1]
    img_width = min(512, 2 * MARGIN + AVATAR_SIZE + PADDING + b_width)
    size = (img_width, 4 * PADDING + b_height)

    x0 = MARGIN + PADDING + AVATAR_SIZE
    x1 = x0 + b_width
    y1 = PADDING + b_height
    points_balloon = Box(x0, PADDING, x1, y1)

    img = Image.new("RGBA", size, transparent)
    dr = ImageDraw.Draw(img)
    draw_avatar(
        img, dr, username, points_balloon=points_balloon, avatar_path=avatar_path
    )

    draw_balloon(dr, points=points_balloon, fill=BOX_COLOR)

    draw_username(
        dr, position=points_balloon.top_left, font=bold_font, username=username
    )
    draw_message(
        dr, points=points_balloon, font=font, text=final_text, user_size=title_size
    )
    draw_time(dr, text=msg_time, points=points_balloon, font=time_font)

    ratio = 512 / img_width
    sample = Image.ANTIALIAS
    img = img.resize((512, int(ratio * size[1])), resample=sample)
    img_path = IMG_DIR / f'{IMG_PREFIX}{user_id}.png'
    img.save(img_path)
    img.close()
    return img_path


def wrapped_text(text: str, line_limit=25):
    words = text.split(' ')
    lines = [words[0]]
    for w in words[1:]:
        if len(lines[-1]) + len(w) < line_limit:
            lines[-1] += ' ' + w
        else:
            lines.append(w)
    return '\n'.join(lines)


def sticker_from_image(jpg_path: str):
    img: Image = Image.open(jpg_path)
    if img.width >= img.height:
        ratio = 512 / img.width
        img = img.resize((512, int(ratio * img.height)), resample=Image.ANTIALIAS)
    else:
        ratio = 512 / img.height
        img = img.resize((int(ratio * img.width), 512), resample=Image.ANTIALIAS)
    img_path = jpg_path[0:-4] + '.png'
    img.save(img_path)
    img.close()
    return img_path


def generate_avatar_mask(img_size: tuple, points: Box):
    img = Image.new("RGBA", img_size, (0, 0, 0, 0))
    maskdraw = ImageDraw.Draw(img)
    maskdraw.ellipse(points.to_list(), fill='#FFFFFF')
    del maskdraw
    return img
