import pygame
import random
import math

class AmbientOrb:
    def __init__(self, screen_width, screen_height, pulse_speed=0.05):
        self.x, self.y = random.randint(0, screen_width), random.randint(0, screen_height)
        self.vx, self.vy = random.uniform(-0.3, 0.3), random.uniform(-0.3, 0.3)
        self.radius = random.randint(1, 2)
        self.color = (200, 255, 200)
        self.base_alpha = 80
        self.alpha_range = 60
        self.time_offset = random.uniform(0, 2 * math.pi)
        self.surface = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.t = 0
        self.pulse_speed = pulse_speed

    def update(self):
        self.t += self.pulse_speed
        self.alpha = int(self.base_alpha + (math.sin(self.t + self.time_offset) * 0.5 + 0.5) * self.alpha_range)
        self.x = (self.x + self.vx) % self.screen_width
        self.y = (self.y + self.vy) % self.screen_height

    def draw(self, screen):
        self.surface.fill((0, 0, 0, 0))
        center = (self.surface.get_width() // 2, self.surface.get_height() // 2)
        pygame.draw.circle(self.surface, (*self.color, self.alpha), center, self.radius * 2)
        pygame.draw.circle(self.surface, (*self.color, 255), center, self.radius)
        screen.blit(self.surface, (self.x - self.radius * 2, self.y - self.radius * 2))
