# src/ui/end_screen.py
import pygame
import os

WIDTH = 800
HEIGHT = 600

class EndScreen:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        assets_path = os.path.join(base_dir, "..", "..", "assets")
        self.image = pygame.image.load(os.path.join(assets_path, "end_screen.PNG")).convert()
        self.image = pygame.transform.scale(self.image, (WIDTH, HEIGHT))
        self.font = pygame.font.Font(None, 25)
        self.text = self.font.render("Press any key to restart", True, (49, 134, 89))
        self.text_rect = self.text.get_rect(center=(WIDTH // 2, HEIGHT - 50))

    def show(self, screen):
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False

            screen.blit(self.image, (0, 0))
            screen.blit(self.text, self.text_rect)
            pygame.display.flip()
