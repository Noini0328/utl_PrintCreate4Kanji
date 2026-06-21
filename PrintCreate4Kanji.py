from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT_PATH = r"C:\Windows\Fonts\msgothic.ttc"

pdfmetrics.registerFont(TTFont("JP", FONT_PATH))

PAGE_W, PAGE_H = A4

# =====================================
# 設定
# =====================================

COLS = 3

MARGIN_X = 20
MARGIN_Y = 25

if COLS == 1:

    BOX_SIZE = 72
    BOX_W = 72

    CHAR_W = 28

    FONT_SIZE = 28
    RUBY_SIZE = 12

    ROW_HEIGHT = 100

elif COLS == 2:

    BOX_SIZE = 48
    BOX_W = 48

    CHAR_W = 20

    FONT_SIZE = 22
    RUBY_SIZE = 10

    ROW_HEIGHT = 68

elif COLS == 3:

    BOX_SIZE = 36
    BOX_W = 36

    CHAR_W = 15

    FONT_SIZE = 16
    RUBY_SIZE = 8

    ROW_HEIGHT = 52

elif COLS == 4:

    BOX_SIZE = 24
    BOX_W = 24

    CHAR_W = 11

    FONT_SIZE = 11
    RUBY_SIZE = 6

    ROW_HEIGHT = 38

elif COLS == 5:

    BOX_SIZE = 18
    BOX_W = 18

    CHAR_W = 9

    FONT_SIZE = 9
    RUBY_SIZE = 5

    ROW_HEIGHT = 30

else:

    BOX_SIZE = 24
    BOX_W = 24

    CHAR_W = 11

    FONT_SIZE = 11
    RUBY_SIZE = 6

    ROW_HEIGHT = 38

GAP = 1

USABLE_WIDTH = PAGE_W - MARGIN_X * 2
COL_WIDTH = USABLE_WIDTH / COLS

# =====================================
# 入力
# =====================================

def parse_line(line):

    line = line.strip()

    if not line:
        return None

    parts = [x.strip() for x in line.split(",")]

    text = parts[0]
    rubies = parts[1:]

    return text, rubies

# =====================================
# トークン化
# =====================================

def tokenize(text):

    result = []

    pos = 0

    while pos < len(text):

        if text[pos] == "*":

            end = text.find("*", pos + 1)

            if end == -1:
                break

            word = text[pos + 1:end]

            result.append(
                ("boxgroup", word)
            )

            pos = end + 1

        else:

            result.append(
                ("char", text[pos])
            )

            pos += 1

    return result

# =====================================
# 横幅計算
# =====================================

def calc_width(text):

    width = 0

    tokens = tokenize(text)

    for typ, value in tokens:

        if typ == "char":

            width += CHAR_W + GAP

        else:

            width += len(value) * (BOX_W + GAP)

    return width

# =====================================
# 描画
# =====================================

def draw_item(c, x, y, text, rubies, mode):

    needed_width = calc_width(text)

    usable_width = COL_WIDTH - 6

    scale = min(
        1.0,
        usable_width / max(needed_width, 1)
    )

    scale = max(scale, 0.65)

    box_w = BOX_W * scale
    char_w = CHAR_W * scale

    font_size = FONT_SIZE * scale
    ruby_size = RUBY_SIZE * scale

    gap = GAP * scale

    tokens = tokenize(text)

    cur_x = x

    ruby_index = 0

    for typ, value in tokens:

        # -------------------
        # 普通文字
        # -------------------

        if typ == "char":

            center_x = cur_x + char_w / 2

            c.setFont(
                "JP",
                font_size
            )

            c.drawCentredString(
                center_x,
                y + font_size * 0.25,
                value
            )

            cur_x += char_w + gap

        # -------------------
        # □グループ
        # -------------------

        else:

            chars = list(value)

            group_start = cur_x

            for ch in chars:

                center_x = cur_x + box_w / 2

                c.rect(
                    cur_x,
                    y,
                    box_w,
                    box_w
                )

                if mode == "boxtrace":

                    trace_font_size = box_w * 0.9

                    c.setFillColor(
                        colors.Color(
                            0.85,
                            0.85,
                            0.85
                        )
                    )

                    c.setFont(
                        "JP",
                        trace_font_size
                    )

                    c.drawCentredString(
                        center_x,
                        y + (box_w - trace_font_size) / 2 + 2,
                        ch
                    )

                    c.setFillColor(
                        colors.black
                    )

                cur_x += box_w + gap

            # -------------------
            # ルビ
            # -------------------

            if ruby_index < len(rubies):

                ruby = rubies[ruby_index]

                ruby_index += 1

                group_width = (
                    len(chars) * box_w
                    + (len(chars) - 1) * gap
                )

                ruby_center = (
                    group_start
                    + group_width / 2
                )

                ruby_y = (
                    y
                    + box_w
                    + max(
                        2,
                        ruby_size * 0.4
                    )
                )

                c.setFont(
                    "JP",
                    ruby_size
                )

                c.drawCentredString(
                    ruby_center,
                    ruby_y,
                    ruby
                )

# =====================================
# PDF
# =====================================

def render(pdf_name, mode, problems):

    c = canvas.Canvas(
        pdf_name,
        pagesize=A4
    )

    rows_per_col = int(
        (PAGE_H - 2 * MARGIN_Y)
        / (ROW_HEIGHT + RUBY_SIZE)
    )
    if COLS ==2:
        rows_per_col = rows_per_col + 1
    if COLS ==3:
        rows_per_col = rows_per_col + 2
    if COLS ==4:
        rows_per_col = rows_per_col + 4
    if COLS ==5:
        rows_per_col = rows_per_col + 4

    row = 0
    col = 0

    for text, rubies in problems:

        x = (
            MARGIN_X
            + col * COL_WIDTH
        )

        y = (
            PAGE_H
            - MARGIN_Y
            - ROW_HEIGHT
            - row * ROW_HEIGHT
        )

        draw_item(
            c,
            x,
            y,
            text,
            rubies,
            mode
        )

        row += 1

        if row >= rows_per_col:

            row = 0
            col += 1

        if col >= COLS:

            c.showPage()

            row = 0
            col = 0

    c.save()

# =====================================
# main
# =====================================

def main():

    problems = []

    with open(
        "input.txt",
        encoding="utf-8"
    ) as f:

        for line in f:

            parsed = parse_line(line)

            if parsed:

                problems.append(parsed)

    print(
        f"{len(problems)} problems loaded"
    )

    render(
        "kanji_test.pdf",
        "test",
        problems
    )

    render(
        "kanji_boxtrace.pdf",
        "boxtrace",
        problems
    )

    print("completed")

if __name__ == "__main__":
    main()