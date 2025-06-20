# src/game/item.py
import pygame
import os
import random

class Item:
    def __init__(self, screen_width, screen_height, tile_size, image_names):
        self.tile_size = tile_size
        self.screen_width = screen_width
        self.screen_height = screen_height

        base_dir = os.path.dirname(os.path.abspath(__file__))
        assets_path = os.path.join(base_dir, "..", "..", "assets")

        self.images = [
            pygame.transform.scale(
                pygame.image.load(os.path.join(assets_path, name)).convert_alpha(),
                (tile_size, tile_size)
            ) for name in image_names
        ]

        self.animation_index = 0
        self.animation_timer = 0
        self.animation_delay = 10

        self.position = self.random_position()

    def random_position(self):
        margin = 3  # margin in tiles
        x = random.randint(margin, self.screen_width // self.tile_size - 1 - margin) * self.tile_size
        y = random.randint(margin, self.screen_height // self.tile_size - 1 - margin) * self.tile_size
        return (x, y)

    def update(self):
        self.animation_timer += 1
        if self.animation_timer >= self.animation_delay:
            self.animation_timer = 0
            self.animation_index = (self.animation_index + 1) % len(self.images)

    def draw(self, surface):
        surface.blit(self.images[self.animation_index], self.position)

    def reset(self):
        self.position = self.random_position()

    def collision(self, snake_head):
        return self.position == snake_head


class Food(Item):
    def __init__(self, screen_width, screen_height, tile_size):
        super().__init__(screen_width, screen_height, tile_size, ["food_sprite1.PNG", "food_sprite2.PNG"])


class Danger(Item):
    def __init__(self, screen_width, screen_height, tile_size):
        super().__init__(screen_width, screen_height, tile_size, ["danger_sprite1.PNG", "danger_sprite2.PNG"])

    def reset_away_from_snake(self, snake_body, min_distance_blocks=5):
        max_attempts = 100
        for _ in range(max_attempts):
            pos = self.random_position()
            too_close = False
            for segment in snake_body:
                dx = abs(pos[0] - segment[0]) // self.tile_size
                dy = abs(pos[1] - segment[1]) // self.tile_size
                if dx <= min_distance_blocks and dy <= min_distance_blocks:
                    too_close = True
                    break
            if not too_close:
                self.position = pos
                return
        self.position = self.random_position()
