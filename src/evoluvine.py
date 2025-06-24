
import pygame
import sys
from constants import *
from src.Brain.model_manager import ModelManager
from src.game.item import Food
from src.game.score import Score
from ui.ambient_orb import AmbientOrb

def create_snake(model_data):
    model_manager = ModelManager()
    return model_manager.create_snake_from_model(model_data, WIDTH, HEIGHT, TILE_SIZE)

def draw_info(surface, font, fitness, screen_width):
    text_surface = font.render(f"Fitness: {fitness:.2f}", True, (255, 255, 255))
    text_rect = text_surface.get_rect(topright=(screen_width - 10, 50))
    surface.blit(text_surface, text_rect)

def main():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Evoluvine AI")
    clock = pygame.time.Clock()

    #aesthetics
    icon = pygame.image.load(ICON_PATH)
    pygame.display.set_icon(icon)
    background = pygame.image.load(BG_PATH)
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    font = pygame.font.SysFont(None, 25)
    orbs = [AmbientOrb(WIDTH, HEIGHT, TILE_SIZE) for _ in range(6)]

    model_manager = ModelManager()
    model_data = model_manager.load_best_model()
    if not model_data:
        print("No saved model found.")
        pygame.quit()
        sys.exit()

    snake = create_snake(model_data)
    food = Food(WIDTH, HEIGHT, TILE_SIZE)
    score = Score()

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if snake.alive:
            snake.update(food)
            if food.collision(snake.head_pos()):
                snake.grow()
                score.increment()
                food.reset()
        else:
            screen.blit(background, (0, 0))
            for orb in orbs:
                orb.update()
                orb.draw(screen)
            snake.draw(screen)
            food.draw(screen)

            score.draw(screen, WIDTH, font)
            draw_info(screen, font, snake.fitness, WIDTH)

            pygame.display.flip()
            pygame.time.delay(2000)

            snake = create_snake(model_data)
            food.reset()
            score.reset()

        screen.blit(background, (0, 0))
        for orb in orbs:
            orb.update()
            orb.draw(screen)
        snake.draw(screen)
        food.update()
        food.draw(screen)

        score.draw(screen, WIDTH, font)
        draw_info(screen, font, snake.fitness, WIDTH)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
