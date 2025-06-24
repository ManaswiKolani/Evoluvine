
import pygame

class Score:
    def __init__(self):
        self.value = 0

    def increment(self):
        self.value += 1

    def reset(self):
        self.value = 0

    def draw(self, surface, screen_width, font):
        text = font.render(f"Score: {self.value}", True, (255, 255, 255))
        surface.blit(text, (screen_width - text.get_width() - 10, 10))