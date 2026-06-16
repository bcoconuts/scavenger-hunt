from constants import (STRINGS as S)
from datetime import date
from exceptions import ManualAbort
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
import math

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
POPUP_HEIGHT = 700
POPUP_WIDTH = 700
MENU_BUTTON_WIDTH = 350
BUTTON_HEIGHT = 30
MENU_SCREEN_BUFFER = 100
GAME_SCREEN_BUFFER = 80
MENU_BORDER_THICKNESS = 6
MENU_BOX_EXPANSION_RATE = 5
MENU_BOX_MIN_EXPANSION_RATE = 1
MENU_BOX_EMPTY_PAUSE = 150
BUTTON_HEIGHT_BUFFER = 7
BUTTON_WIDTH_BUFFER = 30
VERTICAL_FDL_OFFSET = 25
TITLE_BUFFER = 120
MENU_OPTION_FONT_COLOR = (255, 154, 43)
MENU_OPTION_FONT_SIZE = 15
MENU_HEADER_FONT_COLOR = (255, 233, 127)
SHORT_MENU_HEADER_FONT_SIZE = 35
LONG_MENU_HEADER_FONT_SIZE = 15
POPUP_FONT_COLOR = (255, 154, 43)
POPUP_FONT_SIZE = 20
MSG_BUFFER = 15
POPUP_PAUSE = 1000
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
            "menu header font": load_font("Fonts/CS Maria Double.otf", SHORT_MENU_HEADER_FONT_SIZE),
            "menu option font": load_font("Fonts/CS Maria Regular.otf", MENU_OPTION_FONT_SIZE),
            "popup msg font": load_font("Fonts/CS Maria Regular.otf", POPUP_FONT_SIZE)
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
        self.open_box = False
        self.close_box = False


        self.popup_rect = pygame.Rect(
            (
                (SCREEN_WIDTH - POPUP_WIDTH)//2,
                (SCREEN_HEIGHT - POPUP_HEIGHT)//2,
                POPUP_WIDTH,
                POPUP_HEIGHT
            )
        )
        self.closed_popup_rect = pygame.Rect(
            (
                self.popup_rect.width/2 - MENU_BORDER_THICKNESS,
                (self.popup_rect.height - self.fonts["popup msg font"].size("ABCDEFGHIJKLMNOPabcdefghijklmnop!?.,")[1])/2 - MSG_BUFFER,
                MENU_BORDER_THICKNESS*2,
                MENU_BORDER_THICKNESS*2
            )
        )
        self.popup_sect = self.screen.subsurface(self.popup_rect)
        self.popup_sect.set_clip(self.closed_popup_rect)
        self.popup_offset = self.popup_sect.get_offset()
        self.popup_size = pygame.Rect((0, 0, 0, 0))



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
        self.last_menu_fdls: RenderList = list()
        self.last_popup_surfs: RenderList = list()
        self.last_popup_fdls: RenderList = list()
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
    
    @property
    def long_pause_until(self) -> int:
        return pygame.time.get_ticks() + POPUP_PAUSE

    # ======================
    # SCREEN PAINTING
    # ======================

    def _update_screen_scroll(self, surf: Surface, coord_list: list[tuple[float, float]], vert_rate: float, horz_rate: float) -> RenderList:
        render_list = []
        for index, (x, y) in enumerate(coord_list):
            y += vert_rate
            if y > SCREEN_HEIGHT:
                y -= self.scroll_img_height * 3
            x += horz_rate
            if x > SCREEN_WIDTH:
                x -= self.scroll_img_width * 3
            coord_list[index] = (x, y)
            render_list.append((surf, (x,y)))
        return render_list


    def _update_screen_scrolls(self) -> RenderList:
        scrolling_qs = self._update_screen_scroll(self.assets["scrolling qs"], self.scrolling_qs_x_y_pos, VERT_SCROLL_RATE, HORZ_SCROLL_RATE)
        small_scorlling_qs = self._update_screen_scroll(self.assets["small scrolling qs"], self.small_scrolling_qs_x_y_pos, SMALL_VERT_SCROLL_RATE,  SMALL_HORZ_SCROLL_RATE) 
        return scrolling_qs + small_scorlling_qs

    def _update_screen_background(self) -> RenderList:
        return [(self.assets["background"], (0, 0))]


    # ======================
    # MENU PAINTING
    # ======================
    
    def _update_menu_sect_background(self) -> RenderList:
        return [(self.assets["menu box back"], (0, 0))]
    
    def _update_menu_sect_borders(self) -> RenderList:
        menu_sect_clip = self.menu_sect.get_clip()
        horz_border_surf = self.assets["horz menu box border"]
        vert_border_surf = self.assets["vert menu box border"]
        render_list: RenderList = [
            (horz_border_surf, horz_border_surf.get_rect(top=menu_sect_clip.top)),
            (horz_border_surf, horz_border_surf.get_rect(bottom=menu_sect_clip.bottom)),
            (vert_border_surf, vert_border_surf.get_rect(left=menu_sect_clip.left)),
            (vert_border_surf, vert_border_surf.get_rect(right=menu_sect_clip.right))
        ]
    
        return render_list
    
    def _update_menu_sect_fdls(self) -> RenderList:
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

        return render_list


    # ======================
    # POPUP PAINTING
    # ======================
    
    def _update_popup_sect_background(self) -> RenderList:
        return [(self.assets["menu box back"], (0, 0))]
    
    def _update_popup_sect_borders(self) -> RenderList:
        popup_sect_clip = self.popup_sect.get_clip()
        horz_border_surf = self.assets["horz menu box border"]
        vert_border_surf = self.assets["vert menu box border"]
        render_list: RenderList = [
            (horz_border_surf, horz_border_surf.get_rect(top=popup_sect_clip.top)),
            (horz_border_surf, horz_border_surf.get_rect(bottom=popup_sect_clip.bottom)),
            (vert_border_surf, vert_border_surf.get_rect(left=popup_sect_clip.left)),
            (vert_border_surf, vert_border_surf.get_rect(right=popup_sect_clip.right))
        ]
    
        return render_list
    
    def _update_popup_sect_fdls(self) -> RenderList:
        popup_sect_clip = self.popup_sect.get_clip()
        fdl_tl_surf = self.assets["FDL topleft"]
        fdl_tr_surf = self.assets["FDL topright"]
        fdl_bl_surf = self.assets["FDL botleft"]
        fdl_br_surf = self.assets["FDL botright"]

        fdl_tl_rect = fdl_tl_surf.get_rect(
            bottomright=(
                self.popup_offset[0] + popup_sect_clip.topleft[0] + MENU_BORDER_THICKNESS,
                self.popup_offset[1] + popup_sect_clip.topleft[1] + MENU_BORDER_THICKNESS
            )
        )
        fdl_tr_rect = fdl_tr_surf.get_rect(
            bottomleft=(
                self.popup_offset[0] + popup_sect_clip.topright[0] - MENU_BORDER_THICKNESS,
                self.popup_offset[1] + popup_sect_clip.topright[1] + MENU_BORDER_THICKNESS
            )
        )
        fdl_bl_rect = fdl_bl_surf.get_rect(
            topright=(
                self.popup_offset[0] + popup_sect_clip.bottomleft[0] + MENU_BORDER_THICKNESS,
                self.popup_offset[1] + popup_sect_clip.bottomleft[1] - MENU_BORDER_THICKNESS
            )
        )
        fdl_br_rect = fdl_br_surf.get_rect(
            topleft=(
                self.popup_offset[0] + popup_sect_clip.bottomright[0] - MENU_BORDER_THICKNESS,
                self.popup_offset[1] + popup_sect_clip.bottomright[1] - MENU_BORDER_THICKNESS
            )
        )

        render_list: RenderList = [
            (fdl_tl_surf, fdl_tl_rect),
            (fdl_tr_surf, fdl_tr_rect),
            (fdl_bl_surf, fdl_bl_rect),
            (fdl_br_surf, fdl_br_rect)
        ]

        return render_list
    

    def _update_menu(self, position_to_option_text_surfs: dict[Coordinate, Surface], selected: int) -> RenderList:
        menu_render_list: RenderList | None = []
        for i, (position, option_surf) in enumerate(position_to_option_text_surfs.items()):
            option_rect = option_surf.get_rect(center=position)
            button_surf = self.assets["sel menubox"] if i == selected else self.assets["desel menubox"]
            button_rect = button_surf.get_rect(center=position)
            menu_render_list.append((button_surf, button_rect))
            menu_render_list.append((option_surf, option_rect))
        return menu_render_list


    # ======================
    # GENERAL RENDERING
    # ======================
    
    def draw_frame(self, menu_render_list: RenderList | None=None, game_render_list: RenderList | None=None, popup_render_list: RenderList | None=None):
        
        # Render Main Backgrounds
        self.screen.blits(
            self._update_screen_scrolls() +
            self._update_screen_background()
        )

        # Render Menu Section
        if menu_render_list is not None:
            if self.open_box:
                self._adjust_box(self.menu_sect, self.menu_size)
            if self.close_box:
                self._adjust_box(self.menu_sect, self.closed_menu_rect)
            full_menu_render_list = (
                self._update_menu_sect_background() +
                menu_render_list +
                self._update_menu_sect_borders()
            )
            self.last_menu_surfs = full_menu_render_list
            self.last_menu_fdls = self._update_menu_sect_fdls()
        self.menu_sect.blits(self.last_menu_surfs)
        self.screen.blits(self.last_menu_fdls)

        # Render Popup Section
        if popup_render_list is not None:
            if self.open_box:
                self._adjust_box(self.popup_sect, self.popup_size)
            if self.close_box:
                self._adjust_box(self.popup_sect, self.closed_popup_rect)
            full_popup_render_list = (
                self._update_popup_sect_background() +
                popup_render_list +
                self._update_popup_sect_borders()
            )
            self.last_popup_surfs = full_popup_render_list
            self.last_popup_fdls = self._update_popup_sect_fdls()
        self.popup_sect.blits(self.last_popup_surfs)
        self.screen.blits(self.last_popup_fdls)


        
        pygame.display.flip()
        self.clock.tick(60)

    
    # ======================
    # CLASS HELPERS
    # ======================

    def _adjust_box(self, box_surf: Surface, new_rect: Rect) -> bool | None:
        clip = box_surf.get_clip()

        if (clip.width == new_rect.width and clip.height == new_rect.height):
            box_surf.set_clip(new_rect)
            self.open_box = False
            self.close_box = False
            return True

        width_remaining = new_rect.width - clip.width
        height_remaining = new_rect.height - clip.height
        
        width_step = 0
        height_step = 0

        if clip.width != new_rect.width:
            width_step = max(MENU_BOX_MIN_EXPANSION_RATE, abs((width_remaining)/MENU_BOX_EXPANSION_RATE))
            width_step = width_remaining if width_step > abs(width_remaining) else width_step
            width_step = math.copysign(width_step, width_remaining)
        
        if clip.height != new_rect.height:
            height_step = max(MENU_BOX_MIN_EXPANSION_RATE, abs((height_remaining)/MENU_BOX_EXPANSION_RATE))
            height_step = height_remaining if height_step > abs(height_remaining) else height_step
            height_step = math.copysign(height_step, height_remaining)
        
        box_surf.set_clip(
            (
                round(new_rect.left + width_remaining/2),
                clip.top,
                clip.width + width_step,
                clip.height + height_step
            )
        )

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

    def _format_menu_header(self, header: str) -> tuple[Surface, Rect]:
        if self.fonts["menu header font"].size(header)[0] >= self.menu_rect.width - MSG_BUFFER:
            header_surf = self.fonts["menu option font"].render(header, True, MENU_HEADER_FONT_COLOR, wraplength=(self.menu_rect.width - MENU_SCREEN_BUFFER)) #TODO: pick different font
        else:
            header_surf = self.fonts["menu header font"].render(header, True, MENU_HEADER_FONT_COLOR)
        header_rect = header_surf.get_rect(midtop=(self.menu_rect.width//2, BUTTON_HEIGHT_BUFFER*2))
        return header_surf, header_rect



    # ======================
    # GENERIC I/O
    # ======================

    def get_user_str_choice_from_menu(self, target_dict: dict[str, Any], header="OPTIONS") -> str:

        header_surf, header_rect = self._format_menu_header(header)
        
        position_to_option_text_surfs, option_y = self._get_option_render_info(target_dict, header_rect.height)
        
        menu_length = len(target_dict)
        self.menu_size = pygame.Rect(
            (
                self.menu_rect.width//2 - max(header_rect.width//2, MENU_BUTTON_WIDTH//2) - BUTTON_WIDTH_BUFFER,
                0,
                max(header_rect.width, MENU_BUTTON_WIDTH) + BUTTON_WIDTH_BUFFER*2,
                option_y - BUTTON_HEIGHT//2
            )
        )

        menu_render_list = self._update_menu(position_to_option_text_surfs, 0) + [(header_surf, header_rect)]
        self.open_box = True
        while self.open_box:
            self.draw_frame(menu_render_list=menu_render_list)

        selection_dict = {i: k for i, k in enumerate(target_dict)}
        selected = 0
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.QUIT:
                        pygame.quit()
                        exit()
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % menu_length
                        menu_render_list = self._update_menu(position_to_option_text_surfs, selected) + [(header_surf, header_rect)]
                        self.draw_frame(menu_render_list=menu_render_list)
                    elif event.key == pygame.K_UP:
                        selected = (selected - 1) % menu_length
                        menu_render_list = self._update_menu(position_to_option_text_surfs, selected) + [(header_surf, header_rect)]
                        self.draw_frame(menu_render_list=menu_render_list)
                    elif event.key == pygame.K_RETURN:
                        if not self.open_box:
                            self.close_box = True
                            while self.close_box:
                                self.draw_frame(menu_render_list=menu_render_list)
                            wait_time = self.pause_until
                            while pygame.time.get_ticks() < wait_time:
                                self.draw_frame()
                            selection = selection_dict[selected]
                            return selection
                            
            self.draw_frame()
    
    def display_msg(self, msg: str) -> None:
        msg_surf = self.fonts["popup msg font"].render(msg, True, POPUP_FONT_COLOR)
        msg_rect = msg_surf.get_rect(center=(self.popup_rect.centerx - self.popup_offset[0], self.popup_rect.centery - self.popup_offset[1]))
        self.popup_size = pygame.Rect(
            (
                msg_rect.left - MSG_BUFFER,
                msg_rect.top - MSG_BUFFER,
                msg_rect.width + MSG_BUFFER * 2,
                msg_rect.height + MSG_BUFFER * 2
            )
        )
        popup_render_list: RenderList = [(msg_surf, msg_rect)]
        self.open_box = True
        while self.open_box:
            self.draw_frame(popup_render_list=popup_render_list)
        wait_time = self.long_pause_until
        while pygame.time.get_ticks() < wait_time:
            self.draw_frame()
        self.close_box = True
        while self.close_box:
            self.draw_frame(popup_render_list=popup_render_list)
    
    def warn_user(self, warning_msg: str) -> bool:
        choice = self.get_user_str_choice_from_menu({"Yes": "Yes", "No": "No"}, header=warning_msg)
        if choice == "Yes":
            return True
        else:
            self.display_msg("Operation Cancelled.")
            raise ManualAbort

    def greet_user(self) -> None:
        pass

    def get_player_name(self, existing_names: set[str]) -> str:
        pass

            

# ======================
# GENERIC HELPERS
# ======================

def load_image(path: str) -> Surface:
    img = pygame.image.load(BASE_IMG_PATH + path).convert_alpha()
    return img

def load_font(path: str, size: int, is_bold: bool=False, is_underlined: bool=False) -> Font:
    font = pygame.font.Font(BASE_IMG_PATH + path, size)
    font.align = pygame.FONT_CENTER
    if is_bold:
        pygame.font.Font.set_bold(font, True)
    if is_underlined:
        pygame.font.Font.set_underline(font, True)
    return font

def back():
    """Menu action: return False to break out of the current submenu loop."""
    return False
