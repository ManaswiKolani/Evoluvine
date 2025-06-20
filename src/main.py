import pygame
import sys
from ui.title_screen import show_title_screen
from ui.ambient_orb import AmbientOrb
from ui.end_screen import EndScreen
from game.snake import Snake
from game.item import Food, Danger
from game.score import Score
from constants import WIDTH, HEIGHT, FPS, TILE_SIZE, ORB_COUNT, \
                      DANGER_RELOCATE_INTERVAL, DEATH_DELAY, \
                      BG_PATH, ICON_PATH, TITLE_CARD_PATH, MUSIC_PATH

def main():
    pygame.init()
    pygame.mixer.init()

    pygame.mixer.music.load(MUSIC_PATH)
    pygame.mixer.music.set_volume(0.1)
    pygame.mixer.music.play(-1)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Evoluvine🐍")

    background = pygame.image.load(BG_PATH).convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    icon = pygame.image.load(ICON_PATH)
    pygame.display.set_icon(icon)

    title_card = pygame.image.load(TITLE_CARD_PATH).convert_alpha()
    title_card = pygame.transform.scale(title_card, (
        int(title_card.get_width() * 1.5), int(title_card.get_height() * 1.5)))

    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 28)

    orbs = [AmbientOrb(WIDTH, HEIGHT) for _ in range(ORB_COUNT)]
    end_screen = EndScreen()

    while True:
        show_title_screen(screen, background, title_card)

        snake = Snake(start_pos=(WIDTH // 2, HEIGHT // 2), tile_size=TILE_SIZE,
                      screen_width=WIDTH, screen_height=HEIGHT)

        food = Food(WIDTH, HEIGHT, TILE_SIZE)
        danger = Danger(WIDTH, HEIGHT, TILE_SIZE)
        score = Score()
        danger_timer = pygame.time.get_ticks()

        MOVE_DELAY = 8
        move_counter = 0
        death_time = None
        game_over_displayed = False

        running = True
        while running:
            clock.tick(FPS)
            current_time = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            screen.blit(background, (0, 0))

            for orb in orbs:
                orb.update()
                orb.draw(screen)

            if not snake.alive:
                snake.draw(screen)
                if death_time is None:
                    death_time = current_time
                elif current_time - death_time > DEATH_DELAY and not game_over_displayed:
                    end_screen.show(screen)
                    game_over_displayed = True
                    running = False
                pygame.display.flip()
                continue

            keys = pygame.key.get_pressed()
            snake.handle_input(keys)

            move_counter += 1
            if move_counter >= MOVE_DELAY:
                snake.move()
                move_counter = 0

                if food.collision(snake.head_position()):
                    snake.grow()
                    food.reset()
                    score.increment()

                if danger.collision(snake.head_position()):
                    snake.die()

            if current_time - danger_timer >= DANGER_RELOCATE_INTERVAL:
                danger.reset_away_from_snake(snake.body)
                danger_timer = current_time

            snake.draw(screen)
            food.update()
            food.draw(screen)
            danger.update()
            danger.draw(screen)

            score.draw(screen, WIDTH, font)

            pygame.display.flip()

if __name__ == "__main__":
    main()
