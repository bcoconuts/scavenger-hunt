"""
Constants
"""

from datetime import date
from types import SimpleNamespace


DEBUG = False

STRINGS = SimpleNamespace(
    YES="Yes",
    NO="No",
    YEARS="years",
    MONTHS="months",
    CATEGORY="category",
    MAIN_MENU="Main Menu",
    MANAGE_PLAYERS="Manage Players",
    MANAGE_QUESTIONS="Manage Questions",
    MANAGE_SCORES="Manage Scores",
    ANSWER_QUESTIONS="Answer Questions (Play Game)",
    EXIT="Exit",
    ADD_PLAYER="Add Player",
    EDIT_PLAYER="Edit Player",
    REMOVE_PLAYER="Remove Player",
    VIEW_PLAYERS="View Players",
    BACK="Back",
    ASSIGN_NEW_QUESTIONS_TO_PLAYER="Assign New Questions To Player",
    PRINT_QUESTIONS="Create Question PDF",
    DISPLAY_QUESTIONS_FOR_PLAYER="Display Questions For Player",
    DELETE_QUESTIONS_FOR_PLAYER="Delete Questions For Player",
    EDIT_QUESTION_STATUS="Edit Question Status",
    VIEW_SCORES="View Scores",
    DELETE_CURRENT_QUESTIONS_SCORE_HISTORY="Delete Current Question Set Score History",
    DELETE_ALL_SCORE_HISTORY="Delete Score History",
    MULTIPLE_CHOICE="Multiple Choice",
    ASK_AND_ANSWER="Ask & Answer (Parents guide game)",
    UNANSWERED="Unanswered",
    CORRECTLY_ANSWERED="Correctly Answered",
    INCORRECTLY_ANSWERED="Incorrectly Answered",
    MAX_QUESTIONS="Max Questions",
    VALID_QUESTION_NUMBERS="Valid Question Numbers",
    MAX_PLAYERS="Max Players",
    MAX_AGE="Max Age",
    CURRENT_YEAR="Current Date",
    BIRTH_YEAR_RANGE="Birth Year Range",
    VALID_MONTHS="Valid Months",
    PLAYER_FILE_NAME="Player File Name",
    PLAYER="Player",
    QBANK="Qbank",
    PDF_FILE_NAME="PDF File Name",
    ROWS="Rows",
    COLUMNS="Columns",
    DPI="DPI",
    IMG_WRITER_OPTIONS="Image Writer Options",
    TEXT_DISTANCE="text_distance",
    FONT_SIZE="font_size",
    MODULE_HEIGHT="module_height",
    MARGIN_BOTTOM="margin_bottom",
    MARGIN_TOP="margin_top",
    UNIT="Unit",
    PAGE_FORMAT="Page Format",
    PAGE_MARGIN="Page Margin",
    PAGE_TOP="Page Top",
    PAGE_LENGTH="Page Length",
    PAGE_WIDTH="Page Width",
    PAGE_LEFT="Page Left",
    SOLID_DASH_LENGTH="Solid Dash Length",
    GAP="Gap",
    MAX_BARCODE_CHARS="Max Barcode Characters"
)

QUESTION_STATUSES = {
    1: STRINGS.UNANSWERED,
    2: STRINGS.CORRECTLY_ANSWERED,
    3: STRINGS.INCORRECTLY_ANSWERED
}

YES_NO_DICT = {
    1: STRINGS.YES,
    2: STRINGS.NO
}

INTS = {
    STRINGS.MAX_QUESTIONS: 100,
    STRINGS.MAX_PLAYERS: 100,
    STRINGS.MAX_AGE: 100,
    STRINGS.CURRENT_YEAR: date.today().year
}

RANGES = {
    STRINGS.VALID_QUESTION_NUMBERS: {num for num in range(1, INTS[STRINGS.MAX_QUESTIONS] + 1)},
    STRINGS.BIRTH_YEAR_RANGE: set(range(INTS[STRINGS.CURRENT_YEAR] - INTS[STRINGS.MAX_AGE], INTS[STRINGS.CURRENT_YEAR] + 1)),
    STRINGS.VALID_MONTHS: set(range(1, 13))
}

FILE_NAMES = {
    STRINGS.PLAYER_FILE_NAME: "players.json",
    STRINGS.PDF_FILE_NAME: f"_questions_{date.today()}.pdf"
}

PDF_GENERATION = {
    STRINGS.ROWS: 5, # 9 rows maximum before you begin to alter barcode. recommend 5 for children
    STRINGS.COLUMNS: 2, # 2 column maximum before you begin to alter barcode.
    STRINGS.DPI: 72,
    STRINGS.IMG_WRITER_OPTIONS: {
        STRINGS.TEXT_DISTANCE: 1.25,
        STRINGS.FONT_SIZE: 3,
        STRINGS.MODULE_HEIGHT: 5,
        STRINGS.MARGIN_BOTTOM: 0,
        STRINGS.MARGIN_TOP: 1,
    },
    STRINGS.UNIT: "in",
    STRINGS.PAGE_FORMAT: "letter",
    STRINGS.PAGE_MARGIN: 0,
    STRINGS.PAGE_TOP: 0,
    STRINGS.PAGE_LENGTH: 11,
    STRINGS.PAGE_WIDTH: 8.5,
    STRINGS.PAGE_LEFT: 0,
    STRINGS.SOLID_DASH_LENGTH: 0.375,
    STRINGS.GAP: 0.25,
    STRINGS.MAX_BARCODE_CHARS: 22
}