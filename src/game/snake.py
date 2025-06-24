# src/game/snake.py
import pygame
import os

class Snake:
    def __init__(self, start_pos, tile_size, screen_width, screen_height):
        self.tile_size = tile_size
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.body = [start_pos]
        self.direction = (tile_size, 0)  
        self.grow_next = False
        self.alive = True

        # Load snake image
        base_dir = os.path.dirname(os.path.abspath(__file__))
        assets_path = os.path.join(base_dir, "..", "..", "assets")
        self.image = pygame.image.load(os.path.join(assets_path, "snake_live.PNG")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (tile_size, tile_size))

        self.death_image = pygame.image.load(os.path.join(assets_path, "snake_dead.PNG")).convert_alpha()
        self.death_image = pygame.transform.scale(self.death_image, (tile_size, tile_size))

    def handle_input(self, keys):
        if keys[pygame.K_UP] and self.direction != (0, self.tile_size):
            self.direction = (0, -self.tile_size)
        elif keys[pygame.K_DOWN] and self.direction != (0, -self.tile_size):
            self.direction = (0, self.tile_size)
        elif keys[pygame.K_LEFT] and self.direction != (self.tile_size, 0):
            self.direction = (-self.tile_size, 0)
        elif keys[pygame.K_RIGHT] and self.direction != (-self.tile_size, 0):
            self.direction = (self.tile_size, 0)

    def move(self):
        if not self.alive:
            return

        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # Die if out of bounds
        if (new_head[0] < 0 or new_head[0] >= self.screen_width or
            new_head[1] < 0 or new_head[1] >= self.screen_height or
            new_head in self.body):
            self.die()
            return

        self.body.insert(0, new_head)

        if self.grow_next:
            self.grow_next = False
        else:
            self.body.pop()


    def grow(self):
        self.grow_next = True

    def draw(self, surface):
        for segment in self.body:
            img = self.death_image if not self.alive else self.image
            surface.blit(img, segment)

    def head_position(self):
        return self.body[0]

    def die(self):
        self.alive = False
