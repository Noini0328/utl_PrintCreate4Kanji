from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT_PATH = r"C:\Windows\Fonts\msgothic.ttc"

pdfmetrics.registerFont(TTFont("JP", FONT_PATH))

PAGE_W, PAGE_H = A4

# =========================
# レイアウト
# =========================

COLS = 5

MARGIN_X = 20
MARGIN_Y = 25

BOX_SIZE = 24

CHAR_W = 11
BOX_W = 24
GAP = 1

FONT_SIZE = 10
RUBY_SIZE = 6

ROW_HEIGHT = 38
#COL_WIDTH = 135(col4
COL_WIDTH = 110

# =========================
# 入力解析
# =========================

def parse_line(line):

    line = line.strip()

    if not line:
        return None

    if "," in line:
        text, ruby = line.rsplit(",", 1)
        return text.strip(), ruby.strip()

    return line, ""


def tokenize(text):

    result = []

    pos = 0

    while pos < len(text):

        if text.startswith("**", pos):

            end = text.find("**", pos + 2)

            if end == -1:
                break

            word = text[pos + 2:end]

            for ch in word:
                result.append(("box", ch))

            pos = end + 2
            continue

        if text[pos] == "*":

            end = text.find("*", pos + 1)

            if end == -1:
                break

            word = text[pos + 1:end]

            for ch in word:
                result.append(("box", ch))

            pos = end + 1
            continue

        result.append(("char", text[pos]))
        pos += 1

    return result


# =========================
# 描画
# =========================

def draw_item(c, x, y, text, ruby, mode):

    tokens = tokenize(text)

    box_centers = []

    cur_x = x

    for typ, _ in tokens:

        if typ == "box":
            box_centers.append(cur_x + BOX_W / 2)
            cur_x += BOX_W + GAP
        else:
            cur_x += CHAR_W + GAP

    # ---------------------
    # ルビ
    # ---------------------

    if ruby and box_centers:

        if len(box_centers) == 1:
            ruby_x = box_centers[0]
        else:
            ruby_x = (box_centers[0] + box_centers[-1]) / 2

        c.setFont("JP", RUBY_SIZE)

        c.drawCentredString(
            ruby_x,
            y + BOX_SIZE + 4,
            ruby
        )

    # ---------------------
    # 本体
    # ---------------------

    cur_x = x

    for typ, value in tokens:

        if typ == "char":

            center_x = cur_x + CHAR_W / 2

            c.setFont("JP", FONT_SIZE)

            c.drawCentredString(
                center_x,
                y + 6,
                value
            )

            cur_x += CHAR_W + GAP

        else:

            center_x = cur_x + BOX_W / 2

            c.rect(
                cur_x,
                y,
                BOX_W,
                BOX_W
            )

            if mode == "boxtrace":

                c.setFillColor(colors.Color(0.8, 0.8, 0.8))

                c.setFont("JP", FONT_SIZE)

                c.drawCentredString(
                    center_x,
                    y + 6,
                    value
                )

                c.setFillColor(colors.black)

            cur_x += BOX_W + GAP


# =========================
# PDF生成
# =========================

def render(pdf_name, mode, problems):

    c = canvas.Canvas(pdf_name, pagesize=A4)

    rows_per_col = int(
        (PAGE_H - 2 * MARGIN_Y) / ROW_HEIGHT
    )

    row = 0
    col = 0

    for text, ruby in problems:

        x = MARGIN_X + col * COL_WIDTH

        y = (
            PAGE_H
            - MARGIN_Y
            - BOX_SIZE
            - row * ROW_HEIGHT
        )

        draw_item(
            c,
            x,
            y,
            text,
            ruby,
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


# =========================
# main
# =========================

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

    print(f"{len(problems)} problems loaded")

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