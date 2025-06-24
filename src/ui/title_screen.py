import pygame
import sys
from ui.ambient_orb import AmbientOrb

WIDTH = 800
HEIGHT = 600

def show_title_screen(screen, background, title_card):
    font = pygame.font.Font(None, 25)
    text = font.render("Press anywhere to start", True, (49, 134, 89))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False

        screen.blit(background, (0, 0))

        screen.blit(title_card, title_card.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        screen.blit(text, text_rect)
        pygame.display.flip()

