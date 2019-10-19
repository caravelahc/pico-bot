from PIL import Image, ImageDraw, ImageFont
from .config import ROOT_DIR

# for testing purpose only
# ROOT_DIR = '/home/diogo/Documents/CCO/Python/pico-bot/picobot'

IMG_DIR = ROOT_DIR + '/images/'
IMG_NAME = 'img'
AVATAR_MASK_NAME = 'avatar_mask.png'

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
BOX_COLOR = "#182533"
FONT_SIZE = 14
TITLE_COLOR = "#338cf3"
TEXT_COLOR = "#dddddd"
TIME_COLOR = "#6A7B8C"
LINE_SPACE = 4


def draw_balloon(
    img_draw: ImageDraw.Draw, xy: list, fill=None, width=0
):
    r_x0 = xy[0]
    r_y0 = xy[1] + BOX_RADIUS
    r_x1 = xy[2]
    r_y1 = xy[3] - BOX_RADIUS
    img_draw.rectangle(
        [r_x0, r_y0, r_x1, r_y1], fill=fill, width=width
    )
    r_x0 = xy[0] + BOX_RADIUS
    r_y0 = xy[1]
    r_x1 = xy[2] - BOX_RADIUS
    r_y1 = xy[3]
    img_draw.rectangle(
        [r_x0, r_y0, r_x1, r_y1], fill=fill, width=width
    )
    diam = 2 * BOX_RADIUS
    c_x0 = xy[0]
    c_y0 = xy[1]
    c_x1 = c_x0 + diam
    c_y1 = c_y0 + diam
    img_draw.ellipse([c_x0, c_y0, c_x1, c_y1], fill=fill, width=width)
    c_x0 = xy[2] - diam
    c_x1 = c_x0 + diam
    img_draw.ellipse([c_x0, c_y0, c_x1, c_y1], fill=fill, width=width)
    c_y0 = xy[3] - diam
    c_y1 = c_y0 + diam
    img_draw.ellipse([c_x0, c_y0, c_x1, c_y1], fill=fill, width=width)

    arrow_x = 10
    arrow_y = 10 if BOX_RADIUS < 10 else BOX_RADIUS
    x0, y0, x1, y1 = xy
    arrow = [
        (x0 - arrow_x, y1),
        (x0, y1 - arrow_y),
        (x0 + diam, y1 - arrow_y),
        (x0 + diam, y1),
    ]
    img_draw.polygon(arrow, fill=fill)


def draw_username(
    txt_draw: ImageDraw.ImageDraw,
    xy: list,
    username="Jojo",
    fill=TITLE_COLOR,
    font=None,
):
    x0 = xy[0] + MSG_PADDING_H
    y0 = xy[1] + MSG_PADDING_V
    txt_draw.text((x0, y0), username, font=font, fill=fill)


def draw_message(
    txt_draw: ImageDraw.ImageDraw,
    xy: list,
    text="Oi, eu sou o Jojo",
    fill=TEXT_COLOR,
    font=None,
    user_size=[0,0]
):
    x0 = xy[0] + MSG_PADDING_H
    y0 = xy[1] + MSG_PADDING_V + user_size[1] + LINE_SPACE
    txt_draw.text((x0, y0), text, font=font, fill=fill)


def draw_time(
    txt_draw: ImageDraw.ImageDraw,
    xy: list,
    text="04:20",
    fill=TEXT_COLOR,
    font=None
):
    tw = txt_draw.textsize(text, font=font)
    x0 = xy[2] - TIME_PADDING_H - tw[0]
    y0 = xy[3] - (TIME_PADDING_BOTTOM + tw[1])
    txt_draw.text((x0, y0), text, font=font, fill=TIME_COLOR)


def draw_avatar(img, xy_balloon: list, avatar_path: str):
    if avatar_path == '':
        return
    y0 = xy_balloon[3] - AVATAR_SIZE
    y1 = xy_balloon[3]
    xy = [MARGIN, y0, MARGIN + AVATAR_SIZE, y1]
    box = tuple(a-2 for a in xy[0:2])
    size = AVATAR_SIZE + 4
    avatar = Image.open(avatar_path).convert(mode='RGBA')
    if avatar.width == avatar.height:
        avatar = avatar.resize((size, size), resample=Image.ANTIALIAS)
    elif avatar.width > avatar.height:
        ratio = size / avatar.width
        avatar = avatar.resize((size, int(ratio * avatar.height)), resample=Image.ANTIALIAS)
    else:
        ratio = size / avatar.height
        avatar = avatar.resize((int(ratio * avatar.width), size), resample=Image.ANTIALIAS)

    avatar_mask = generate_avatar_mask(img.size, xy)
    tmp = Image.new('RGBA', img.size)
    tmp.paste(avatar, box=box)
    img.paste(tmp, mask=avatar_mask)


def sticker_from_text(user_id: int, username: str, text: str, avatar_path: str, msg_time: str):
    size = (512, 256)
    transparent = (0, 0, 0, 0)

    FONT_DIR = ROOT_DIR + '/fonts/'
    bold_font = ImageFont.truetype(font=f"{FONT_DIR}OpenSans-Bold.ttf", size=16)
    font = ImageFont.truetype(font=f"{FONT_DIR}OpenSans-SemiBold.ttf", size=16)
    time_font = ImageFont.truetype(font=f"{FONT_DIR}OpenSans-Regular.ttf", size=13)

    username = username if (len(username) < 26) else f'{username[0:25]}...'
    limit_is_user = (len(username) >= len(text))
    aux_img = ImageDraw.Draw(Image.new('RGBA', size, transparent))
    title_size = aux_img.textsize(username, font=bold_font)
    text_size = aux_img.textsize(text, font=font)
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
    box_size = (bigger_size[0] + 2 * MSG_PADDING_H,
                title_size[1] + bigger_size[1] + 2 * MSG_PADDING_V + time_size[1] + 2 * LINE_SPACE)

    b_width = max(BOX_MIN_WIDTH, box_size[0])
    b_height = box_size[1]
    img_width = min(512, 2 * MARGIN + AVATAR_SIZE + PADDING + b_width)
    size = (img_width, 4 * PADDING + b_height)

    x0 = MARGIN + PADDING + AVATAR_SIZE
    x1 = x0 + b_width
    y1 = PADDING + b_height
    xy_balloon = [x0, PADDING, x1, y1]

    img = Image.new("RGBA", size, transparent)
    dr = ImageDraw.Draw(img)
    draw_avatar(img, xy_balloon=xy_balloon, avatar_path=avatar_path)

    draw_balloon(dr, xy=xy_balloon, fill=BOX_COLOR)

    draw_username(dr, xy=xy_balloon, font=bold_font, username=username)
    draw_message(dr, xy=xy_balloon, font=font, text=final_text, user_size=title_size)
    draw_time(dr, text=msg_time, xy=xy_balloon, font=time_font)

    ratio = 512 / img_width
    sample = Image.ANTIALIAS
    img = img.resize((512, int(ratio * size[1])), resample=sample)
    img_path = IMG_DIR + IMG_NAME + str(user_id) + '.png'
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


def generate_avatar_mask(img_size: tuple, xy: list):
    img = Image.new("RGBA", img_size, (0, 0, 0, 0))
    maskdraw = ImageDraw.Draw(img)
    maskdraw.ellipse(xy, fill='#FFFFFF')
    del maskdraw
    return img
