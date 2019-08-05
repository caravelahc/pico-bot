from PIL import Image, ImageDraw, ImageFont
# from .config import ROOT_DIR

# for testing purpose only
ROOT_DIR = '/home/diogo/Documents/CCO/Python/pico-bot/picobot'

IMG_DIR = ROOT_DIR + '/images/'
IMG_NAME = 'img'
AVATAR_MASK_NAME = 'avatar_mask.png'

AVATAR_SIZE = 36
MARGIN = 4
PADDING = 10
MSG_PADDING_H = 12
MSG_PADDING_V = 8
TIME_PADDING = 16
BOX_HEIGHT = 50
BOX_MIN_WIDTH = 160
BOX_MAX_WIDTH = 430
BOX_RADIUS = 10
BOX_COLOR = "#182533"
FONT_SIZE = 14
TITLE_COLOR = "#338cf3"
TEXT_COLOR = "#dddddd"
TIME_COLOR = "#6A7B8C"
LINE_HEIGHT = 12


def draw_balloon(
    img_draw: ImageDraw.Draw, xy: list, fill=None, width=0,
    outline=None, radius=0
):
    r_x0 = xy[0]
    r_y0 = xy[1] + radius
    r_x1 = xy[2]
    r_y1 = xy[3] - radius
    img_draw.rectangle(
        [r_x0, r_y0, r_x1, r_y1], outline=outline, fill=fill, width=width
    )
    r_x0 = xy[0] + radius
    r_y0 = xy[1]
    r_x1 = xy[2] - radius
    r_y1 = xy[3]
    img_draw.rectangle(
        [r_x0, r_y0, r_x1, r_y1], outline=outline, fill=fill, width=width
    )
    diam = 2 * radius
    c_x0 = xy[0]
    c_y0 = xy[1]
    c_x1 = c_x0 + diam
    c_y1 = c_y0 + diam
    img_draw.ellipse([c_x0, c_y0, c_x1, c_y1], fill=fill, outline=outline, width=width)
    c_x0 = xy[2] - diam
    c_x1 = c_x0 + diam
    img_draw.ellipse([c_x0, c_y0, c_x1, c_y1], fill=fill, outline=outline, width=width)
    c_y0 = xy[3] - diam
    c_y1 = c_y0 + diam
    img_draw.ellipse([c_x0, c_y0, c_x1, c_y1], fill=fill, outline=outline, width=width)

    arrow_x = 10
    arrow_y = 10 if radius < 10 else radius
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
):
    x0 = xy[0] + MSG_PADDING_H
    y0 = xy[1] + (2 * MSG_PADDING_V) + LINE_HEIGHT
    txt_draw.text((x0, y0), text, font=font, fill=fill)


def draw_time(
    txt_draw: ImageDraw.ImageDraw, xy: list, text="04:20", fill=TEXT_COLOR, font=None
):
    x0 = xy[2] - (MSG_PADDING_H * 4)
    y0 = xy[3] - (MSG_PADDING_V + LINE_HEIGHT)
    txt_draw.text((x0, y0), text, font=font, fill=TIME_COLOR)


def draw_avatar(img, avatar_path: str):
    y0 = BOX_HEIGHT + PADDING - AVATAR_SIZE
    y1 = BOX_HEIGHT + PADDING
    xy = [MARGIN, y0, MARGIN + AVATAR_SIZE, y1]
    box = tuple(a-2 for a in xy[0:2])
    if avatar_path == '':
        return
    size = AVATAR_SIZE + 4
    avatar = Image.open(avatar_path).convert(mode='RGBA')
    if avatar.width >= avatar.height:
        ratio = size / avatar.width
        avatar = avatar.resize((size, int(ratio * avatar.height)), resample=Image.ANTIALIAS)
    else:
        ratio = size / avatar.height
        avatar = avatar.resize((int(ratio * avatar.width), size), resample=Image.ANTIALIAS)

    avatar_mask = generate_avatar_mask(img.size)
    tmp = Image.new('RGBA', img.size)
    tmp.paste(avatar, box=box)
    img.paste(tmp, mask=avatar_mask)


def sticker_from_text(user_id: int, username: str, text: str, avatar_path: str):
    size = (512, 2 * PADDING + BOX_HEIGHT)
    transparent = (0, 0, 0, 0)

    FONT_DIR = ROOT_DIR + '/fonts/'
    bold_font = ImageFont.truetype(font=f"{FONT_DIR}OpenSans-Bold.ttf", size=13)
    font = ImageFont.truetype(font=f"{FONT_DIR}OpenSans-Regular.ttf", size=13)

    aux_text = username if (len(username) >= len(text)) else text
    aux_text += '88:88'
    aux_font = bold_font if (len(username) >= len(text)) else font
    aux = ImageDraw.Draw(Image.new('RGBA', size, transparent))
    box_width = aux.textsize(aux_text, font=aux_font)[0] + 2 * MSG_PADDING_H + TIME_PADDING
    box_width = max(BOX_MIN_WIDTH, min(box_width, BOX_MAX_WIDTH))
    img_width = min(512, 2 * MARGIN + AVATAR_SIZE + PADDING + box_width)
    size = (img_width, size[1])

    img = Image.new("RGBA", size, transparent)
    dr = ImageDraw.Draw(img)
    draw_avatar(img, avatar_path)

    x0 = MARGIN + PADDING + AVATAR_SIZE
    x1 = x0 + box_width
    y1 = PADDING + BOX_HEIGHT
    xy = [x0, PADDING, x1, y1]
    draw_balloon(dr, xy=xy, fill=BOX_COLOR, radius=BOX_RADIUS)

    draw_username(dr, xy=xy, font=bold_font, username=username)
    draw_message(dr, xy=xy, font=font, text=text)
    draw_time(dr, xy=xy, font=font)

    ratio = 512 / img_width
    sample = Image.ANTIALIAS
    img = img.resize((512, int(ratio * size[1])), resample=sample)

    img_path = IMG_DIR + IMG_NAME + str(user_id) + '.png'
    img.save(img_path)
    img.close()
    return img_path


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


def generate_avatar_mask(size: tuple):
    y0 = BOX_HEIGHT + PADDING - AVATAR_SIZE
    y1 = BOX_HEIGHT + PADDING
    xy = [MARGIN, y0, MARGIN + AVATAR_SIZE, y1]

    img = Image.new("RGBA", size, (0,0,0,0))
    maskdraw = ImageDraw.Draw(img)
    maskdraw.ellipse(xy, fill='#FFFFFF')
    del maskdraw
    return img


if __name__ == "__main__":
    # sticker_from_text(46, "Tarcísio Eduardo Moreira Crocomo", "Haha")
    generate_avatar_mask()
