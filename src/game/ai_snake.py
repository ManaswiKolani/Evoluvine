import pygame
import numpy as np
import math

class AISnake:
    def __init__(self, start_pos, tile_size, screen_width, screen_height, brain = None):
        self.tile_size = tile_size
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.body = [start_pos]
        self.direction = (tile_size, -0) 
        self.alive = True
        self.brain = brain
        self.growth_pending = 0
        self.fitness = 0
        self.steps = 0
        self.food_eaten = 0
        self.last_food_distance = None



    def head_position(self):
        return self.body[0]
        
    def move(self):
        if not self.alive:
            return

        new_head = (self.body[0][0] + self.direction[0],
                    self.body[0][1] + self.direction[1])

        # Die if out of bounds
        if (new_head[0] < 0 or new_head[0] >= self.screen_width or
            new_head[1] < 0 or new_head[1] >= self.screen_height or
            new_head in self.body):
            self.alive = False
            return

        self.body.insert(0, new_head)

        if self.growth_pending > 0:
            self.growth_pending -= 1
        else:
            self.body.pop()

        self.steps += 1


    def grow(self):
        self.growth_pending += 1
        self.food_eaten += 1
            
    def die(self):
        self.alive = False
            
    def check_environment(self, food, danger):
        head_x, head_y = self.head_position()

        food_x, food_y = food.position
        danger_x, danger_y = danger.position

        food_dx = (food_x - head_x) / self.screen_width
        food_dy = (food_y - head_y) / self.screen_height
        danger_dx = (danger_x - head_x) / self.screen_width
        danger_dy = (danger_y - head_y) / self.screen_height

        dir_x = self.direction[0] / self.tile_size
        dir_y = self.direction[1] / self.tile_size

        return np.array([food_dx, food_dy, danger_dx, danger_dy, dir_x, dir_y])

    def make_decision(self, inputs):
        if self.brain is None:
            return
            
        outputs = self.brain.feedforward(inputs)
        idx = np.argmax(outputs)
        directions = [(0, -self.tile_size), (0, self.tile_size), (-self.tile_size, 0), (self.tile_size, 0)]
        new_direction = directions[idx]

        if len(self.body) > 1 and (new_direction[0] == -self.direction[0] and new_direction[1] == -self.direction[1]):
            return
            
        self.direction = new_direction

    def update(self, food, danger):
        if not self.alive:
            return

        inputs = self.check_environment(food, danger)
        self.make_decision(inputs)
        self.move()

        self.fitness += 1 + self.food_eaten * 20  # survival + food reward

        # Distance to food
        head_x, head_y = self.head_position()
        food_x, food_y = food.position
        distance = math.hypot(food_x - head_x, food_y - head_y)
        max_distance = math.hypot(self.screen_width, self.screen_height)

        # Reward or penalize based on distance change
        if self.last_food_distance is not None:
            if distance < self.last_food_distance:
                self.fitness += 5  # moved closer
            else:
                self.fitness -= 1  # moved away

        self.last_food_distance = distance

    def draw(self, surface, highlight=False):
        color = (255, 0, 0) if highlight else (0, 255, 0)
        for segment in self.body:
            pygame.draw.rect(surface, color, pygame.Rect(segment[0], segment[1], self.tile_size, self.tile_size))

        