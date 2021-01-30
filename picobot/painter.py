import textwrap
from pathlib import Path

from emoji import emoji_lis, emoji_count
from PIL import Image, ImageDraw, ImageFont

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
    LINE_WIDTH_LIMIT,
    MAX_NUMBER_OF_LINES,
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

FONTS = {
    'bold': ImageFont.truetype(
        font=str(FONT_DIR / 'OpenSans-Bold.ttf'), size=FONT_SIZE
    ),
    'normal': ImageFont.truetype(
        font=str(FONT_DIR / 'OpenSans-SemiBold.ttf'), size=FONT_SIZE
    ),
    'time': ImageFont.truetype(font=str(FONT_DIR / 'OpenSans-Regular.ttf'), size=13),
    'emoji': ImageFont.truetype(font=str(FONT_DIR / 'Symbola.ttf'), size=16),
    'avatar': ImageFont.truetype(font=str(FONT_DIR / 'OpenSans-SemiBold.ttf'), size=20),
}


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
    username="Caravela",
    fill=TITLE_COLOR,
):
    x0 = position.x + MSG_PADDING_H
    y0 = position.y + MSG_PADDING_V
    txt_draw.text((x0, y0), username, font=FONTS['bold'], fill=fill)


def draw_message(
    txt_draw: ImageDraw.ImageDraw, points: Box, text=' ', user_size=[0, 0],
):
    current_position = Point(
        points.top_left.x + MSG_PADDING_H,
        points.top_left.y + MSG_PADDING_V + user_size[1] + LINE_SPACE,
    )
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
            font=FONTS['emoji'],
            fill=TEXT_COLOR,
        )
        incr = 1
        if len(text) > em['location'] + 1 and text[em['location'] + 1] == EMOJI_JOINER:
            incr = 2
        indexes.append(em['location'] + incr)
        current_position.x += txt_draw.textsize(current_text, font=FONTS['emoji'])[0]

    def draw_text(text: str):
        lines = text.split('\n')
        y_displacement = txt_draw.textsize(' ', font=FONTS['normal'])[1] + LINE_SPACE
        for line in lines[:-1]:
            txt_draw.text(
                current_position.to_tuple(),
                text=line,
                font=FONTS['normal'],
                fill=TEXT_COLOR,
            )
            current_position.x = points.top_left.x + MSG_PADDING_H
            current_position.y += y_displacement
        text = lines[-1]
        txt_draw.text(
            current_position.to_tuple(),
            text=text,
            font=FONTS['normal'],
            fill=TEXT_COLOR,
        )
        displacement = txt_draw.textsize(text, font=FONTS['normal'])
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


def draw_time(txt_draw: ImageDraw.ImageDraw, points: Box, text="04:20"):
    tw = txt_draw.textsize(text, font=FONTS['time'])
    x0 = points.bottom_right.x - TIME_PADDING_H - tw[0]
    y0 = points.bottom_right.y - (TIME_PADDING_BOTTOM + tw[1])
    txt_draw.text((x0, y0), text, font=FONTS['time'], fill=TIME_COLOR)


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
        avatar_center = points.center().to_tuple()
        draw.text(
            avatar_center,
            username[0],
            anchor='mm',
            font=FONTS['avatar'],
            fill='#FFFFFF',
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
    '''
    Creates an image from a text message, emulating Telegram's message layout/design.
    '''
    size = (512, 256)
    transparent = (0, 0, 0, 0)

    username = username if (len(username) < 26) else f'{username[0:25]}...'
    limit_is_user = len(username) >= len(text)
    aux_img = ImageDraw.Draw(Image.new('RGBA', size, transparent))
    title_size = aux_img.textsize(username, font=FONTS['bold'])
    text_size = aux_img.textsize(text, font=FONTS['normal'])
    additional_space_for_emojis = 5 * emoji_count(text)
    text_size = (text_size[0] + additional_space_for_emojis, text_size[1])
    time_size = aux_img.textsize('04:20', font=FONTS['time'])
    final_text = text

    if limit_is_user:
        bigger_size = title_size
    else:
        if len(text) >= LINE_WIDTH_LIMIT:
            aux_text = wrapped_text(text, line_width=LINE_WIDTH_LIMIT)
            final_text, text_size = try_better_aspect_ratio(
                aux_img, original_text=text, modified_text=aux_text
            )
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

    draw_username(dr, position=points_balloon.top_left, username=username)
    draw_message(dr, points=points_balloon, text=final_text, user_size=title_size)
    draw_time(dr, text=msg_time, points=points_balloon)

    img = resize_to_sticker_limits(img)
    img_path = IMG_DIR / f'{IMG_PREFIX}{user_id}.png'
    img.save(img_path)
    img.close()
    return img_path


def wrapped_text(text: str, line_width=25, max_lines=None):
    return '\n'.join(textwrap.wrap(text, width=line_width, max_lines=max_lines))


def try_better_aspect_ratio(img: ImageDraw, original_text: str, modified_text: str):
    '''
    If the message text is too long, wrapping it in 25 character lines will result in an image with a big height and small width, making it difficult to read when resized to Telegram's limit of 512px.
    So if the wrapped text has a height more than two times its width, we increase the line width limit and re-wrap it until we get an aspect ratio closer to 1:1.
    '''
    line_width = LINE_WIDTH_LIMIT
    text_size = img.multiline_textsize(modified_text, font=FONTS['normal'])
    for _ in range(3):
        if text_size[1] > 2 * text_size[0]:
            line_width *= 2
            modified_text = wrapped_text(
                original_text, line_width=line_width, max_lines=MAX_NUMBER_OF_LINES
            )
            text_size = img.multiline_textsize(modified_text, font=FONTS['normal'])
        else:
            break
    return modified_text, text_size


def sticker_from_image(jpg_path: Path):
    '''
    Converts the given image to a proper format that can be uploaded as a sticker.
    Telegram accepts PNG images with a maximum size of 512x512 pixels.
    '''
    with Image.open(jpg_path) as img:
        img = resize_to_sticker_limits(img)
        img_path = jpg_path.with_suffix('.png')
        img.save(img_path)
    return img_path


def resize_to_sticker_limits(img: Image):
    '''
    Resizes the image to fit Telegram restrictions (maximum size of 512x512 pixels), keeping its aspect ratio.
    '''
    if img.width >= img.height:
        ratio = 512 / img.width
        img = img.resize((512, int(ratio * img.height)), resample=Image.ANTIALIAS)
    else:
        ratio = 512 / img.height
        img = img.resize((int(ratio * img.width), 512), resample=Image.ANTIALIAS)
    return img


def generate_avatar_mask(img_size: tuple, points: Box):
    img = Image.new("RGBA", img_size, (0, 0, 0, 0))
    maskdraw = ImageDraw.Draw(img)
    maskdraw.ellipse(points.to_list(), fill='#FFFFFF')
    del maskdraw
    return img
