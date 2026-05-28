import pygame

q_id = "870814"
question = "This thing working?"
q_dict = {q_id: question}
code = ""

pygame.init()

screen = pygame.display.set_mode((1000, 500))

clock = pygame.time.Clock()

text_font = pygame.font.Font(None, 25)

# SURFACES

prompt_surf = text_font.render("Scan Barcode", False, "White")
prompt_rect = prompt_surf.get_rect(midbottom = (500, 50))

question_surf = text_font.render(None, False, "White")
question_rect = question_surf.get_rect(midbottom = (500, 450))

button1_surf = pygame.Surface((200, 100))
button1_surf.fill((225, 0, 0))
button1_rect = button1_surf.get_rect(midbottom = (300, 250))

button2_surf = pygame.Surface((200, 100))
button2_surf.fill((225, 0, 0))
button2_rect = button1_surf.get_rect(midbottom = (700, 250))


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # scanner sends Enter at the end of the code
                if code in q_dict:
                    question_surf = text_font.render(q_dict[code], False, "White")
                    question_rect = question_surf.get_rect(midbottom = (500, 450))
                code = ""
            elif event.unicode.isdigit():
                code += event.unicode

    screen.fill("Black")
    screen.blit(prompt_surf, prompt_rect)
    screen.blit(button1_surf, button1_rect)
    screen.blit(button1_surf, button2_rect)
    screen.blit(question_surf, question_rect)
    pygame.display.flip()
    clock.tick(60)
