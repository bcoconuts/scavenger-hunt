"""Generate pdf for Code128 barcodes that are encoding 8 digits of information.
Pdf has barcodes evenly spaced with as much padding as possible for as many rows 
and columns as are selected.
"""

from barcode import Code128
from barcode.writer import ImageWriter
from constants import (
    STRINGS as S,
    PDF_GENERATION as PDF,
    FILE_NAMES
)
from datetime import date
from fpdf import FPDF
from io import BytesIO
from PIL import Image
import os


def generate_pdf(player_name: str, question_id_list: list[str], category: str, filepath: str | None=None) -> str:
    pdf = FPDF(unit=PDF[S.UNIT], format=PDF[S.PAGE_FORMAT])
    pdf.set_margin(PDF[S.PAGE_MARGIN])
    pdf.add_page()
    _add_barcodes(pdf, player_name, question_id_list, category)
    _draw_grid(pdf)
    if os.path.isdir(str(filepath)):
        filepath = f"{filepath}{player_name}{FILE_NAMES[S.PDF_FILE_NAME]}"
    else:
        filepath = f"{player_name}{FILE_NAMES[S.PDF_FILE_NAME]}"
    pdf.output(filepath)
    return filepath


def _add_barcodes(pdf: FPDF, player_name: str, question_id_list: list[str], category: str) -> None:
    cell_h = PDF[S.PAGE_LENGTH]/PDF[S.ROWS]
    text_str = _generate_text_str(player_name, category)
    column1_flag = True
    for q_id in question_id_list:
        barcode_img = _generate_barcode(q_id, text_str)
        barcode_w_whitespace_img = _add_whitespace(barcode_img)
        if column1_flag:
            column2_y = pdf.get_y()
            pdf.image(barcode_w_whitespace_img)
        else:
            if column2_y + cell_h > PDF[S.PAGE_LENGTH]:
                column2_y = 0
            pdf.image(barcode_w_whitespace_img, x=4.25, y=column2_y)
        column1_flag = not column1_flag
        if pdf.will_page_break(cell_h):
            _draw_grid(pdf)


def _generate_text_str(player_name: str, category: str) -> str:
    name_str = player_name
    cat_str = category
    current_date_str = str(date.today().month) + "-" + str(date.today().day)
    new_name = False
    new_cat = False
    while len(name_str + cat_str + current_date_str) > PDF[S.MAX_BARCODE_CHARS]:
        if len(cat_str) > PDF[S.MAX_BARCODE_CHARS]//3 - 3:
            cat_str = cat_str[:-1]
            new_cat = True
        elif len(name_str) > PDF[S.MAX_BARCODE_CHARS]//3 - 3:
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
            options=PDF[S.IMG_WRITER_OPTIONS],
            text=text_str
        )
        return Image.open(img_bytes)


def _add_whitespace(image: Image.Image) -> Image.Image:
    w, h = image.size
    new_w, new_h = (
        int(PDF[S.PAGE_WIDTH]/PDF[S.COLUMNS]*PDF[S.DPI]//1),
        int(PDF[S.PAGE_LENGTH]/PDF[S.ROWS]*PDF[S.DPI]//1)
    )
    image_w_whitespace = Image.new("RGB", (new_w // 1, new_h // 1), "white")
    image_w_whitespace.paste(
        image,
        box=((new_w - w) // 2, (new_h - h) // 2) # center the image
    )
    return image_w_whitespace


def _draw_grid(pdf: FPDF) -> None:
    cell_w = PDF[S.PAGE_WIDTH]/PDF[S.COLUMNS]
    cell_h = PDF[S.PAGE_LENGTH]/PDF[S.ROWS]
    start_w = cell_w
    start_h = cell_h
    pdf.set_draw_color(175)
    if PDF[S.COLUMNS] > 1:
        for _ in range(PDF[S.COLUMNS] - 1):
            pdf.dashed_line(
                start_w, PDF[S.PAGE_TOP], start_w, PDF[S.PAGE_LENGTH],
                PDF[S.SOLID_DASH_LENGTH], PDF[S.GAP]
            )
            start_w += cell_w
    if PDF[S.ROWS] > 1:
        for _ in range(PDF[S.ROWS] - 1):
            pdf.dashed_line(
                PDF[S.PAGE_LEFT], start_h, PDF[S.PAGE_WIDTH], start_h,
                PDF[S.SOLID_DASH_LENGTH], PDF[S.GAP]
            )
            start_h += cell_h