import json
import os
import random
from barcode import Code128
from barcode.writer import ImageWriter
from dotenv import load_dotenv
from datetime import date
from fpdf import FPDF
from io import BytesIO
from pydantic import BaseModel, Field, computed_field
from utils import (
    get_unique_alpha_response,
    get_valid_int_response,
    get_user_choice_from_menu,
    get_yes_no_response
)
from uuid import uuid4
from xai_sdk import Client
from xai_sdk.chat import user
from PIL import Image

#PDF GENERATION
X_BUFFER = .415
Y_BUFFER = 0
BAR_WIDTH = 3.42
BAR_HEIGTH = 3.89
COLUMN_SEPARATION = X_BUFFER*2
ROW_SEPARATION = 0.125
NAME_LENGTH = 12
CAT_LENGTH = 20

# FILES
PLAYER_FILE_NAME = "players.json"
PDF_FILE_NAME = f"_questions_{date.today()}.pdf"



# ======================
# PDF GENERATION
# ======================

def generate_pdf() -> FPDF:
    pdf = FPDF(unit="in", format="letter")
    text_str = "XXXXXXXXXXXXXXXXXXXXXXXXXX" # 26 chars
    question_list = ["68005416", "78005416", "88005416", "98005416", "68005416", "78005416", "88005416", "98005416", "68005416", "78005416", "88005416", "98005416", "68005416", "78005416", "98005416", "68005416", "78005416", "88005416", "98005416", "68005416", "78005416", "78005416", "88005416", "98005416", "68005416", "78005416"]
    column1_flag = True
    pdf.set_margin(0)
    pdf.add_page()
    for question in question_list:
        img_bytes = BytesIO()
        Code128(question, ImageWriter()).write(
            img_bytes,
            options={'text_distance': 1.5, 'font_size': 3},
            text=text_str
        )
        barcode_img = Image.open(img_bytes).crop((25, 100, 221, 207)) # cut the top of the barcode off, since it is too tall
        w, h = barcode_img.size
        new_w, new_h = (int(8.5/2*72//1), int(11/5*72//1)) # half a page width (4.25 in) * 72 dpi, 1/5 page length (2.2 in) * 72 dpi
        barcode_w_whitespace_img = Image.new("RGB", (new_w // 1, new_h // 1), "white")
        barcode_w_whitespace_img.paste(barcode_img, ((new_w - w) // 2, (new_h - h) // 2)) # center the image
        if column1_flag:
            column2_y = pdf.get_y()
            print(column2_y)
            pdf.image(barcode_w_whitespace_img)
        else:
            if pdf.will_page_break(new_h):
                column2_y = 0
            pdf.image(barcode_w_whitespace_img, x=4.25, y=column2_y)
        column1_flag = not column1_flag
    
    return pdf

cell_h = 2.2
cell_w = 4.25
solid_dash_length = 0.375
page_top = 0
page_bottom = 11
page_right = 8.5
page_left = 0
gap = 0.25
start_h = cell_h
img_bytes = BytesIO()
pdf = FPDF(unit="in", format="letter")
pdf.add_page()
pdf.set_draw_color(200)
# pdf.start_section()
pdf.set_margin(0)
pdf.set_font("Times")
pdf.dashed_line(cell_w, page_top, cell_w, page_bottom, solid_dash_length, gap)
for num in range(4):
    pdf.dashed_line(page_left, start_h, page_right, start_h, solid_dash_length, gap)
    start_h += cell_h
for num in range(1):
    Code128("12345679", ImageWriter()).write(
                img_bytes,
                options={
                     "text_distance": 1.25,
                     "font_size": 3,
                    "module_height": 5,
                    "margin_bottom": 0,
                    "margin_top": 0,
                },
                # text="XXXXXXXXXXXx"
            )
    image_new = Image.open(img_bytes)
    pdf.image(image_new)
print(image_new.size)
pdf.output("test.pdf")
print(ImageWriter().dpi)
print(ImageWriter().module_height)
print(ImageWriter().module_width)
print(ImageWriter().guard_height_factor)
print(ImageWriter().margin_bottom)
print(ImageWriter().margin_top)
print(ImageWriter().quiet_zone)
