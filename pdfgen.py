"""Generate pdf for Code128 barcodes that are encoding 8 digits of information.
Pdf has barcodes evenly spaced with as much padding as possible for as many rows 
and columns as are selected.
"""

from barcode import Code128
from barcode.writer import ImageWriter
from datetime import date
from fpdf import FPDF
from io import BytesIO
from models import Player, QuestionBank
from PIL import Image


ROWS = 5 # 9 rows maximum before you begin to alter barcode. recommend 5 for children
COLUMNS = 2 # 2 column maximum before you begin to alter barcode.
DPI = 72
IMG_WRITER_OPTIONS = {
    "text_distance": 1.25,
    "font_size": 3,
    "module_height": 5,
    "margin_bottom": 0,
    "margin_top": 1,
}
UNIT = "in"
PAGE_FORMAT = "letter"
PAGE_MARGIN = 0
PAGE_TOP = 0
PAGE_LENGTH = 11
PAGE_WIDTH = 8.5
PAGE_LEFT = 0
SOLID_DASH_LENGTH = 0.375
GAP = 0.25
MAX_BARCODE_CHARS = 22



def generate_pdf(player: Player, question_bank: QuestionBank) -> FPDF:
    pdf = FPDF(unit=UNIT, format=PAGE_FORMAT)
    pdf.set_margin(PAGE_MARGIN)
    pdf.add_page()
    _add_barcodes(pdf, player, question_bank)
    _draw_grid(pdf)
    
    return pdf


def _add_barcodes(pdf: FPDF, player: Player, question_bank: QuestionBank) -> None:
    cell_h = PAGE_LENGTH/ROWS
    text_str = _generate_text_str(player, question_bank)
    column1_flag = True
    for q in question_bank.question_list:
        barcode_img = _generate_barcode(q.question_id, text_str)
        barcode_w_whitespace_img = _add_whitespace(barcode_img)
        if column1_flag:
            column2_y = pdf.get_y()
            pdf.image(barcode_w_whitespace_img)
        else:
            if column2_y + cell_h > PAGE_LENGTH:
                column2_y = 0
            pdf.image(barcode_w_whitespace_img, x=4.25, y=column2_y)
        column1_flag = not column1_flag
        if pdf.will_page_break(cell_h):
            _draw_grid(pdf)


def _generate_text_str(player: Player, question_bank: QuestionBank) -> str:
    name_str = player.name 
    cat_str = question_bank.category
    current_date_str = str(date.today().month) + "-" + str(date.today().day)
    new_name = False
    new_cat = False
    while len(name_str + cat_str + current_date_str) > MAX_BARCODE_CHARS:
        if len(cat_str) > MAX_BARCODE_CHARS//3 - 3:
            cat_str = cat_str[:-1]
            new_cat = True
        elif len(name_str) > MAX_BARCODE_CHARS//3 - 3:
            name_str = name_str[:-1]
            new_name = True
        else:
            break
    if new_cat:
        cat_str = cat_str + "..."
    if new_name:
        name_str = name_str + "..."
    str_list = [name_str, cat_str, current_date_str]
    text_str = " - ".join(str_list)
    return text_str


def _generate_barcode(code: str, text_str: str | None=None) -> Image.Image:
        img_bytes = BytesIO()
        Code128(code, ImageWriter()).write(
            img_bytes,
            options=IMG_WRITER_OPTIONS,
            text=text_str
        )
        return Image.open(img_bytes)


def _add_whitespace(image: Image.Image) -> Image.Image:
    w, h = image.size
    new_w, new_h = (
        int(PAGE_WIDTH/COLUMNS*DPI//1),
        int(PAGE_LENGTH/ROWS*DPI//1)
    )
    image_w_whitespace = Image.new("RGB", (new_w // 1, new_h // 1), "white")
    image_w_whitespace.paste(
        image,
        box=((new_w - w) // 2, (new_h - h) // 2) # center the image
    )
    return image_w_whitespace


def _draw_grid(pdf: FPDF) -> None:
    cell_w = PAGE_WIDTH/COLUMNS
    cell_h = PAGE_LENGTH/ROWS
    start_w = cell_w
    start_h = cell_h
    pdf.set_draw_color(175)
    if COLUMNS > 1:
        for _ in range(COLUMNS - 1):
            pdf.dashed_line(
                start_w, PAGE_TOP, start_w, PAGE_LENGTH,
                SOLID_DASH_LENGTH, GAP
            )
            start_w += cell_w
    if ROWS > 1:
        for _ in range(ROWS - 1):
            pdf.dashed_line(
                PAGE_LEFT, start_h, PAGE_WIDTH, start_h,
                SOLID_DASH_LENGTH, GAP
            )
            start_h += cell_h