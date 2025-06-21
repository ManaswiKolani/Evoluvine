import pygame
import sys
from Brain.genetic_algorithm import GeneticAlgorithm
from game.item import Food, Danger
from ui.ambient_orb import AmbientOrb
from constants import WIDTH, HEIGHT, TILE_SIZE, FPS, ORB_COUNT, BG_PATH, MODEL_PATH , DANGER_RELOCATE_INTERVAL
import pickle

# Configuration
POPULATION_SIZE = 600
INPUT_SIZE = 6
HIDDEN_LAYERS = [6,10,4]
OUTPUT_SIZE = 4
GENERATION_TIME = 1000

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake AI Training")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 25)

# Load background and ambient orbs
background = pygame.image.load(BG_PATH)
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
orbs = [AmbientOrb(WIDTH, HEIGHT, TILE_SIZE) for _ in range(ORB_COUNT)]

# Initialize genetic algorithm
ga = GeneticAlgorithm(POPULATION_SIZE, INPUT_SIZE, HIDDEN_LAYERS, OUTPUT_SIZE,
                      WIDTH, HEIGHT, TILE_SIZE)
generation = 1

# Track best score ever across all generations
best_score_ever = 0

def draw_info(surface, gen, alive_count, best_score, best_score_ever):
    text = font.render(f"Gen: {gen}  Alive: {alive_count}  Gen Score: {best_score} Best Score: {best_score_ever}", True, (255, 255, 255))
    surface.blit(text, (10, 10))

# Main training loop
# Main training loop
while True:
    snakes = ga.get_population()
    food = Food(WIDTH, HEIGHT, TILE_SIZE)
    danger = Danger(WIDTH, HEIGHT, TILE_SIZE)
    danger_timer = pygame.time.get_ticks()

    step_count = 0
    best_score = 0
    running = True
    best_snake = None

    while running:
        clock.tick(FPS)
        step_count += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        alive_count = 0
        for snake in snakes:
            if snake.alive:
                snake.update(food, danger)
                if food.collision(snake.head_position()):
                    snake.grow()
                    food.reset()
                if danger.collision(snake.head_position()):
                    snake.die()
                alive_count += 1

        # Update best_snake and top snakes
        visible_snakes = sorted([s for s in snakes if s.alive], key=lambda s: s.fitness, reverse=True)[:10]
        if visible_snakes:
            best_snake = visible_snakes[0]
            best_score = best_snake.food_eaten
            best_score_ever = max(best_score_ever, best_score)

        # Drawing
        screen.blit(background, (0, 0))
        for orb in orbs:
            orb.update()
            orb.draw(screen)

        food.update()
        food.draw(screen)
        danger.update()
        danger.draw(screen)

        # Draw visible snakes (top 100 or all alive if fewer)
        for i, snake in enumerate(visible_snakes[:100]):
            snake.draw(screen, highlight=(i == 0))

        # Relocate danger if time
        current_time = pygame.time.get_ticks()
        if current_time - danger_timer >= DANGER_RELOCATE_INTERVAL:
            if best_snake:
                danger.reset_away_from_snake(food.position, best_snake.body)
            else:
                danger.reset()
            danger_timer = current_time

        draw_info(screen, generation, alive_count, best_score, best_score_ever)
        pygame.display.flip()

        if alive_count == 0 or step_count > GENERATION_TIME:
            if best_snake:
                with open(MODEL_PATH, 'wb') as f:
                    pickle.dump(best_snake.brain, f)

            generation += 1
            ga.next_generation()
            running = False

