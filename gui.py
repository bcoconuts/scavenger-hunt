from constants import (STRINGS as S)
from datetime import date
from typing import Any
from utils import (
    days_in_month,
    format_info,
)
import pygame
from pygame import (
    Surface,
    Rect  
)
from pygame.font import Font
from typing import Union, Sequence

# ======================
# CUSTOM TYPES
# ======================

Coordinate = tuple[int, int]
RectValue = Union[pygame.Rect, tuple[int, int, int, int], tuple[Coordinate, Coordinate]]
RenderList = list[tuple[Surface, Union[Rect, Coordinate]]]


# ======================
# CONFIG
# ======================

BASE_IMG_PATH = "assets/"
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
MENU_BUTTON_WIDTH = 350
BUTTON_HEIGHT = 30
MENU_SCREEN_BUFFER = 100
GAME_SCREEN_BUFFER = 80
MENU_BORDER_THICKNESS = 6
MENU_BOX_EXPANSION_RATE = 20
MENU_BOX_EMPTY_PAUSE = 100
BUTTON_HEIGHT_BUFFER = 7
BUTTON_WIDTH_BUFFER = 30
VERTICAL_FDL_OFFSET = 25
TITLE_BUFFER = 120
MENU_OPTION_FONT_COLOR = (255, 154, 43)
MENU_OPTION_FONT_SIZE = 15
MENU_HEADER_FONT_COLOR = (255, 233, 127)
MENU_HEADER_FONT_SIZE = 35
VERT_SCROLL_RATE = .75
HORZ_SCROLL_RATE = .1
SMALL_VERT_SCROLL_RATE = .5
SMALL_HORZ_SCROLL_RATE = .5



# ======================
# CLASSES
# ======================

class UIDisplay:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH , SCREEN_HEIGHT), pygame.NOFRAME)
        self.clock = pygame.time.Clock()
        self.assets = {
            "sel menubox": load_image("button_1.png"),
            "desel menubox": load_image("button_2.png"),
            "scrolling qs": load_image("question_mark_foreground1.png"),
            "small scrolling qs": load_image("question_mark_foreground2.png"),
            "background": load_image("border_background.png"),
            "FDL topright": load_image("Fleur_de_lis_topright.png"),
            "FDL topleft": load_image("Fleur_de_lis_topleft.png"),
            "FDL botright": load_image("Fleur_de_lis_botright.png"),
            "FDL botleft": load_image("Fleur_de_lis_botleft.png"),
            "menu box back": load_image("menu_box_background.png"),
            "horz menu box border": load_image("horz_menu_box_border.png"),
            "vert menu box border": load_image("vert_menu_box_border.png")

        }
        self.fonts = {
            "menu header font": load_font("Fonts/CS Maria Double.otf", MENU_HEADER_FONT_SIZE),
            "menu option font": load_font("Fonts/CS Maria Regular.otf", MENU_OPTION_FONT_SIZE),
        }

        self.menu_rect = pygame.Rect(
            (
                MENU_SCREEN_BUFFER,
                MENU_SCREEN_BUFFER + TITLE_BUFFER + VERTICAL_FDL_OFFSET,
                SCREEN_WIDTH//2 - MENU_SCREEN_BUFFER * 2,
                SCREEN_HEIGHT - TITLE_BUFFER - MENU_SCREEN_BUFFER * 2 - VERTICAL_FDL_OFFSET
            )
        )
        self.closed_menu_rect = pygame.Rect(
            (
                self.menu_rect.width//2 - MENU_BORDER_THICKNESS,
                0,
                MENU_BORDER_THICKNESS*2,
                MENU_BORDER_THICKNESS*2
            )
        )
        self.menu_sect = self.screen.subsurface(self.menu_rect)
        self.menu_sect.set_clip(self.closed_menu_rect)
        self.menu_offset = self.menu_sect.get_offset()
        self.menu_size = pygame.Rect((0, 0, 0, 0))
        self.open_menu = False
        self.close_menu = False
        self.menu_is_closed = True

        self.game_rect = pygame.Rect(
            (
                SCREEN_WIDTH//2 + GAME_SCREEN_BUFFER,
                GAME_SCREEN_BUFFER,
                SCREEN_WIDTH//2 - GAME_SCREEN_BUFFER * 2,
                SCREEN_HEIGHT - GAME_SCREEN_BUFFER * 2
            )
        )
        self.game_sect = self.screen.subsurface(self.game_rect)

        self.last_menu_surfs: RenderList = list()
        self.last_game_surfs: RenderList = []
        
        self.scroll_img_height = self.assets["scrolling qs"].get_height()
        self.scroll_img_width = self.assets["scrolling qs"].get_width()
        x_y: list[tuple[float, float]] = []
        for num in range(-1, 2):
            for other_num in range(3):
                x_y.append((num * self.scroll_img_width, other_num * self.scroll_img_height))
        self.scrolling_qs_x_y_pos = x_y
        self.small_scrolling_qs_x_y_pos = list(x_y)

    @property
    def pause_until(self) -> int:
        return pygame.time.get_ticks() + MENU_BOX_EMPTY_PAUSE

    # ======================
    # SCREEN PAINTING
    # ======================

    def _update_screen_scroll(self, surf: Surface, coord_list: list[tuple[float, float]], vert_rate: float, horz_rate: float) -> None:
        for index, (x, y) in enumerate(coord_list):
            self.screen.blit(surf, (x, y))
            y += vert_rate
            if y > SCREEN_HEIGHT:
                y -= self.scroll_img_height * 3
            x += horz_rate
            if x > SCREEN_WIDTH:
                x -= self.scroll_img_width * 3
            coord_list[index] = (x, y)


    def _update_screen_scrolls(self) -> None:
        self._update_screen_scroll(self.assets["scrolling qs"], self.scrolling_qs_x_y_pos, VERT_SCROLL_RATE, HORZ_SCROLL_RATE)
        self._update_screen_scroll(self.assets["small scrolling qs"], self.small_scrolling_qs_x_y_pos, SMALL_VERT_SCROLL_RATE,  SMALL_HORZ_SCROLL_RATE) 

    def _update_screen_background(self) -> None:
        self.screen.blit(self.assets["background"], (0, 0))
    
    def _paint_screen(self) -> None:
        self._update_screen_scrolls()
        self._update_screen_background()


    # ======================
    # MENU BOX PAINTING
    # ======================
    
    def _update_menu_sect_background(self) -> None:
        self.menu_sect.blit(self.assets["menu box back"], (0, 0))
    
    def _update_menu_sect_borders(self) -> None:
        menu_sect_clip = self.menu_sect.get_clip()
        horz_border_surf = self.assets["horz menu box border"]
        vert_border_surf = self.assets["vert menu box border"]
        render_list: RenderList = [
            (horz_border_surf, horz_border_surf.get_rect()),
            (horz_border_surf, horz_border_surf.get_rect(bottom=menu_sect_clip.height)),
            (vert_border_surf, vert_border_surf.get_rect(left=menu_sect_clip.left)),
            (vert_border_surf, vert_border_surf.get_rect(right=menu_sect_clip.right))
        ]
    
        self.menu_sect.blits(render_list)

    
    def _update_menu_sect_fdls(self) -> None:
        menu_sect_clip = self.menu_sect.get_clip()
        fdl_tl_surf = self.assets["FDL topleft"]
        fdl_tr_surf = self.assets["FDL topright"]
        fdl_bl_surf = self.assets["FDL botleft"]
        fdl_br_surf = self.assets["FDL botright"]

        fdl_tl_rect = fdl_tl_surf.get_rect(
            bottomright=(
                self.menu_offset[0] + menu_sect_clip.topleft[0] + MENU_BORDER_THICKNESS,
                self.menu_offset[1] + menu_sect_clip.topleft[1] + MENU_BORDER_THICKNESS
            )
        )
        fdl_tr_rect = fdl_tr_surf.get_rect(
            bottomleft=(
                self.menu_offset[0] + menu_sect_clip.topright[0] - MENU_BORDER_THICKNESS,
                self.menu_offset[1] + menu_sect_clip.topright[1] + MENU_BORDER_THICKNESS
            )
        )
        fdl_bl_rect = fdl_bl_surf.get_rect(
            topright=(
                self.menu_offset[0] + menu_sect_clip.bottomleft[0] + MENU_BORDER_THICKNESS,
                self.menu_offset[1] + menu_sect_clip.bottomleft[1] - MENU_BORDER_THICKNESS
            )
        )
        fdl_br_rect = fdl_br_surf.get_rect(
            topleft=(
                self.menu_offset[0] + menu_sect_clip.bottomright[0] - MENU_BORDER_THICKNESS,
                self.menu_offset[1] + menu_sect_clip.bottomright[1] - MENU_BORDER_THICKNESS
            )
        )

        render_list: RenderList = [
            (fdl_tl_surf, fdl_tl_rect),
            (fdl_tr_surf, fdl_tr_rect),
            (fdl_bl_surf, fdl_bl_rect),
            (fdl_br_surf, fdl_br_rect)
        ]

        self.screen.blits(render_list)

    def _open_menu_box(self) -> RenderList | None:
        menu_sect_clip = self.menu_sect.get_clip()
        if menu_sect_clip.height < self.menu_size.height:
            self.menu_sect.set_clip(
                (
                    menu_sect_clip.left - MENU_BOX_EXPANSION_RATE,
                    menu_sect_clip.top,
                    menu_sect_clip.width + MENU_BOX_EXPANSION_RATE * 2,
                    menu_sect_clip.height + MENU_BOX_EXPANSION_RATE
                )
            )
        else:
            self.open_menu = False

    
    def _close_menu_box(self) -> RenderList | None:
        menu_sect_clip = self.menu_sect.get_clip()
        if menu_sect_clip.height > self.closed_menu_rect.height:
            self.menu_sect.set_clip(
                (
                    menu_sect_clip.left + MENU_BOX_EXPANSION_RATE,
                    menu_sect_clip.top,
                    menu_sect_clip.width - MENU_BOX_EXPANSION_RATE * 2,
                    menu_sect_clip.height - MENU_BOX_EXPANSION_RATE
                )
            )
        else:
            self.close_menu = False

        


    # ======================
    # GENERAL RENDERING
    # ======================
    
    def draw_frame(self, menu_render_list: RenderList | None=None, game_render_list: RenderList | None=None):
        
        self._paint_screen()
        self._update_menu_sect_background()

        if self.open_menu:
            self._open_menu_box()
        if self.close_menu:
            self._close_menu_box()
        if menu_render_list is not None:
            self.last_menu_surfs = menu_render_list
        self.menu_sect.blits(self.last_menu_surfs)
        self._update_menu_sect_borders()
        self._update_menu_sect_fdls()

        
        pygame.display.flip()
        self.clock.tick(60)

        

    
    # ======================
    # CLASS HELPERS
    # ======================

    def  _get_option_render_info(self, target_iterable, header_height: int) -> tuple[dict[Coordinate, Surface], int]:
        position_to_option_text_surfs = {}
        max_option_text_width = MENU_BUTTON_WIDTH - BUTTON_WIDTH_BUFFER
        option_x = (self.menu_rect.width//2)
        option_y = (BUTTON_HEIGHT//2) + (BUTTON_HEIGHT_BUFFER * 3) + header_height
        for option in target_iterable:
            option_center = (option_x, option_y)
            option_text_surf = self.fonts["menu option font"].render(option, True, MENU_OPTION_FONT_COLOR)
            option_text_width = option_text_surf.get_width()
            while option_text_width > max_option_text_width:
                option = option[:-4] + "..."
                option_text_surf = self.fonts["menu option font"].render(option, True, MENU_OPTION_FONT_COLOR)
                option_text_width = option_text_surf.get_width()
            position_to_option_text_surfs[option_center] = option_text_surf
            option_y += BUTTON_HEIGHT + (BUTTON_HEIGHT_BUFFER * 2)
        return position_to_option_text_surfs, option_y

    # ======================
    # GENERIC I/O
    # ======================

    def get_user_str_choice_from_menu(self, target_dict: dict[str, Any], values: bool=False, header="OPTIONS") -> str:
        if values:
            new_dict = target_dict.values()
        else:
            new_dict = target_dict

        header_surf = self.fonts["menu header font"].render(header, True, MENU_HEADER_FONT_COLOR)
        header_rect = header_surf.get_rect(midtop=(self.menu_rect.width//2, BUTTON_HEIGHT_BUFFER*2))
        header_height = MENU_HEADER_FONT_SIZE
        position_to_option_text_surfs, option_y = self._get_option_render_info(new_dict, header_height)
        
        
        menu_length = len(new_dict)
        self.menu_size = pygame.Rect(
            (
                self.menu_rect.width//2 - max(header_rect.width//2, MENU_BUTTON_WIDTH//2) - BUTTON_WIDTH_BUFFER,
                0,
                max(header_rect.width, MENU_BUTTON_WIDTH) + BUTTON_WIDTH_BUFFER*2,
                option_y - BUTTON_HEIGHT//2
            )
        )

        self.open_menu = True
        selection_dict = {i: k for i, k in enumerate(new_dict)}
        selected = 0
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % menu_length
                    elif event.key == pygame.K_UP:
                        selected = (selected - 1) % menu_length
                    elif event.key == pygame.K_RETURN:
                        self.close_menu = True
                        selection = selection_dict[selected]        
                        running = False

            menu_render_list: RenderList = [(header_surf, header_rect)]
            for i, (position, option_surf) in enumerate(position_to_option_text_surfs.items()):
                option_rect = option_surf.get_rect(center=position)
                button_surf = self.assets["sel menubox"] if i == selected else self.assets["desel menubox"]
                button_rect = button_surf.get_rect(center=position)
                menu_render_list.append((button_surf, button_rect))
                menu_render_list.append((option_surf, option_rect))

            self.draw_frame(menu_render_list)

        while self.close_menu:
            self.draw_frame(menu_render_list)
        wait_time = self.pause_until
        while pygame.time.get_ticks() < wait_time:
            self.draw_frame(menu_render_list)
        return selection
            
            

# ======================
# GENERIC HELPERS
# ======================

def load_image(path: str) -> Surface:
    img = pygame.image.load(BASE_IMG_PATH + path).convert_alpha()
    return img

def load_font(path: str, size: int, is_bold: bool=False, is_underlined: bool=False) -> Font:
    font = pygame.font.Font(BASE_IMG_PATH + path, size)
    if is_bold:
        pygame.font.Font.set_bold(font, True)
    if is_underlined:
        pygame.font.Font.set_underline(font, True)
    return font

def back():
    """Menu action: return False to break out of the current submenu loop."""
    return False


ui = UIDisplay()

main_menu = {
    S.ANSWER_QUESTIONS: {
        S.MULTIPLE_CHOICE: "lambda: play_game(session, ui, is_ask_answer=False)",
        S.ASK_AND_ANSWER: "lambda: play_game(session, ui, is_ask_answer=True)",
        S.BACK: back
    },
    S.MANAGE_PLAYERS: {
        S.ADD_PLAYER: "lambda: display_msg()",
        S.EDIT_PLAYER: "lambda: edit_player(session, ui)",
        S.REMOVE_PLAYER: "lambda: remove_player(session, ui)",
        S.VIEW_PLAYERS: "lambda: view_players(session, ui)",
        S.BACK: back
    },
    S.MANAGE_QUESTIONS: {
        S.ASSIGN_NEW_QUESTIONS_TO_PLAYER: "lambda: start_new_run_for_player(session, ui)",
        S.PRINT_QUESTIONS: "lambda: generate_question_pdf(session, ui)",
        S.DISPLAY_QUESTIONS_FOR_PLAYER: "lambda: display_questions_for_player(session, ui)",
        S.DELETE_QUESTIONS_FOR_PLAYER: "lambda: delete_question(session, ui)",
        S.EDIT_QUESTION_STATUS: "lambda: edit_question_status(session, ui)",
        S.BACK: back
    },
    S.MANAGE_SCORES: {
        S.VIEW_SCORES: "lambda: view_scores(session, ui)",
        S.DELETE_SCORE_HISTORY: "lambda: delete_score_history(session, ui)",
        S.BACK: back
    },
    S.EXIT: exit,
}

main_running = True
while main_running:
    choice = ui.get_user_str_choice_from_menu(main_menu, header=S.MAIN_MENU)
    if choice == S.EXIT:
        main_running = main_menu[choice]()
    else:
        running = True
        while running:
            sub_choice = ui.get_user_str_choice_from_menu(main_menu[choice], header=choice)
            try:
                running = main_menu[choice][sub_choice]()
            except Exception:
                running = True