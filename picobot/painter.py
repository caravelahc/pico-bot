from PIL import Image, ImageDraw, ImageFont

AVATAR_SIZE = 36
PADDING = 10
MSG_PADDING_H = 12
MSG_PADDING_V = 8
BOX_HEIGHT = 50
BOX_WIDTH = 260
BOX_RADIUS = 10
BOX_COLOR = '#182533'
FONT_SIZE = 14
TITLE_COLOR = '#338cf3'
TEXT_COLOR = '#dddddd'
TIME_COLOR = '#6A7B8C'
LINE_HEIGHT = 12

def draw_round_rectangle(img_draw: ImageDraw.Draw, \
        xy: list, \
        fill=None, width=0, \
        outline=None, radius=0):
    r_x0 = xy[0]
    r_y0 = xy[1] + radius
    r_x1 = xy[2]
    r_y1 = xy[3] - radius
    img_draw.rectangle([r_x0, r_y0, r_x1, r_y1], outline=outline, fill=fill, width=width)
    r_x0 = xy[0] + radius
    r_y0 = xy[1]
    r_x1 = xy[2] - radius
    r_y1 = xy[3]
    img_draw.rectangle([r_x0, r_y0, r_x1, r_y1], outline=outline, fill=fill, width=width)
    diam = 2*radius
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
    arrow = [(x0-arrow_x, y1), (x0, y1-arrow_y), (x0+diam, y1-arrow_y), (x0+diam, y1)]
    img_draw.polygon(arrow, fill=fill)
    

def draw_username(txt_draw: ImageDraw.ImageDraw, xy: list, username='Jojo', fill=TITLE_COLOR, font=None):
    x0 = xy[0] + MSG_PADDING_H
    y0 = xy[1] + MSG_PADDING_V
    txt_draw.text((x0, y0), username, font=font, fill=fill)


def draw_message(txt_draw: ImageDraw.ImageDraw, xy: list, text='Oi, eu sou o Jojo', fill=TEXT_COLOR, font=None):
    x0 = xy[0] + MSG_PADDING_H
    y0 = xy[1] + (2 * MSG_PADDING_V) + LINE_HEIGHT
    txt_draw.text((x0, y0), text, font=font, fill=fill)


def draw_time(txt_draw: ImageDraw.ImageDraw, xy: list, text='04:20', fill=TEXT_COLOR, font=None):
    x0 = xy[2] - (MSG_PADDING_H * 4)
    y0 = xy[3] - (MSG_PADDING_V + LINE_HEIGHT)
    txt_draw.text((x0, y0), text, font=font, fill=TIME_COLOR)

def draw_avatar(img_draw: ImageDraw.ImageDraw, avatar):
    y0 = BOX_HEIGHT + PADDING - AVATAR_SIZE
    y1 = BOX_HEIGHT + PADDING
    xy = [PADDING, y0, PADDING + AVATAR_SIZE, y1]
    img_draw.ellipse(xy)


def sticker_from_text(username: str, text: str, avatar=''):
    size = (4*PADDING + AVATAR_SIZE + BOX_WIDTH, 2 * PADDING + BOX_HEIGHT)
    transparent = (0,0,0,0)
    img = Image.new('RGBA', size, transparent)
    dr = ImageDraw.Draw(img)
    draw_avatar(dr, avatar)

    x0 = 2 * PADDING + AVATAR_SIZE
    x1 = x0 + BOX_WIDTH
    y1 = PADDING + BOX_HEIGHT
    xy = [x0, PADDING, x1, y1]
    draw_round_rectangle(dr, xy=xy, \
        fill=BOX_COLOR, radius=BOX_RADIUS)
    
    bold_font = ImageFont.truetype(font='fonts/OpenSans-Bold.ttf', size=13)
    font = ImageFont.truetype(font='fonts/OpenSans-Regular.ttf', size=13)
    draw_username(dr, xy=xy, font=bold_font, username=username)
    draw_message(dr, xy=xy, font=font, text=text)
    draw_time(dr, xy=xy, font=font)
    img.save('qqer.png')


if __name__ == '__main__':
    sticker_from_text('Joao das Neves', 'Oi meus queridos!')
