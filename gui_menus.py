import pygame
from constants import STRINGS as S
from pygame.font import Font 
from pygame import Surface
from sys import exit
from typing import Any


SCREEN_WIDTH = 500
SCREEN_HEIGHT = 1000
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 80
SCREEN_BUFFER = 50
BUTTON_BUFFER = 25
FONT_COLOR = "White"

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH , SCREEN_HEIGHT))

clock = pygame.time.Clock()

text_font = pygame.font.Font(None, 25)


def back():
    """Menu action: return False to break out of the current submenu loop."""
    return False


def get_user_str_choice_from_menu(target_dict: dict[str, Any],
                                  header="OPTIONS",
                                  selected_button_img: str="/home/bb/Documents/pyprojects/scavenger-hunt/assets/button_1.png",
                                  deselected_button_image: str="/home/bb/Documents/pyprojects/scavenger-hunt/assets/button_2.png",
                                  screen_width: int=SCREEN_WIDTH,
                                  screen_height: int=SCREEN_HEIGHT,
                                  screen: Surface=pygame.display.set_mode((SCREEN_WIDTH , SCREEN_HEIGHT)),
                                  screen_buffer: int=50,
                                  button_buffer: int=10,
                                  button_height: int | None=None,
                                  button_width: int | None=None,
                                  font: Font=pygame.font.Font(None, 25),
                                  font_color: str="White",
    ) -> str:

    menu_length = len(target_dict)

    header_font = pygame.font.Font(None, 50)
    header_surf = header_font.render(header, 1, font_color)
    header_height = header_surf.get_height()
    
    

    selected_button_surf = pygame.image.load(selected_button_img).convert()    
    deselected_button_surf = pygame.image.load(deselected_button_image).convert()
    
    button_max_width = (screen_width - (screen_buffer * 2) - (button_buffer * 2))
    button_max_height = (screen_height - header_height - (screen_buffer * 2) - (button_buffer * 2 * (menu_length + 1)))//menu_length
    if button_height is None:
        button_height = selected_button_surf.get_height()
    if button_height > button_max_height:
        print("button too tall")
        return ""
    if font.render("QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopoasdfghjklzxcvbnm", 0, font_color).get_height() > (button_height + button_buffer):
        print("text too tall for button. Shrink text size or expand button size if possible.")
        return ""
    if button_width is None:
        button_width = selected_button_surf.get_width()
    if button_width > button_max_width:
        print("button too wide")
        return ""

    header_rect = header_surf.get_rect(topleft=((screen_buffer), (screen_buffer)))

    position_to_option_text_surfs: dict[tuple[int, int], Surface] = {}
    max_option_text_width = button_width - button_buffer
    option_x = (screen_buffer) + (button_width//2)
    option_y = (button_height//2) + screen_buffer + (button_buffer * 3) + header_height
    for option in target_dict:
        option_center = (option_x, option_y)
        option_text_surf = font.render(option, 1, font_color)
        option_text_width = option_text_surf.get_width()
        while option_text_width > max_option_text_width:
            option = option[:-4] + "..."
            option_text_surf = font.render(option, 1, font_color)
            option_text_width = option_text_surf.get_width()
        position_to_option_text_surfs[option_center] = option_text_surf
        option_y += button_height + (button_buffer * 2)
    

    selection_dict = {i: k for i, k in enumerate(target_dict)}
    selected = 0
    while True:
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
                    return selection_dict[selected]
    

        screen.fill("Black")
        screen.blit(header_surf, header_rect)


        for i, (position, option_surf) in enumerate(position_to_option_text_surfs.items()):
            rect_center = option_surf.get_rect(center=position)
            surf = selected_button_surf if i == selected else deselected_button_surf
            surf_rect = surf.get_rect(center=position)
            screen.blit(surf, surf_rect)
            screen.blit(option_surf, rect_center)
        
        
        pygame.display.flip()
        clock.tick(60)



main_menu = {
    S.MANAGE_PLAYERS: {
        S.ADD_PLAYER: "lambda: add_player(session, ui)",
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
    S.ANSWER_QUESTIONS: {
        S.MULTIPLE_CHOICE: "lambda: play_game(session, ui, is_ask_answer=False)",
        S.ASK_AND_ANSWER: "lambda: play_game(session, ui, is_ask_answer=True)",
        S.BACK: back
    },
    S.EXIT: exit
}

main_running = True
while main_running:
    choice = get_user_str_choice_from_menu(main_menu, header=S.MAIN_MENU)
    if choice == S.EXIT:
        main_running = main_menu[choice]()
    else:
        running = True
        while running:
            sub_choice = get_user_str_choice_from_menu(main_menu[choice], header=choice)
            try:
                running = main_menu[choice][sub_choice]()
            except Exception:
                running = True