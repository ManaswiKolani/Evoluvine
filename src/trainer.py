import pygame
import sys
import numpy as np
import os
import json
import pickle
from datetime import datetime
from constants import *
from src.Brain.genetic_algorithm import GeneticAlgorithm
from src.game.item import Food
from ui.ambient_orb import AmbientOrb
from src.Brain.model_manager import ModelManager

POPULATION_SIZE = 250
INPUT_SIZE = 4  # [forward_danger, left_danger, right_danger, food_angle_sin]
HIDDEN_SIZE = 6 # Neurons in Hidden Layer
OUTPUT_SIZE = 3  # [forward, left, right]
GENERATION_LIMIT = 150
ORB_COUNT = 6
MAX_STEPS_PER_SNAKE = 1000 # Time out per generation

EARLY_STOP_FITNESS = 15000  # Stop training if this fitness is achieved

model_manager = ModelManager()

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake AI Training")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 18)

background = pygame.image.load(BG_PATH)
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
orbs = [AmbientOrb(WIDTH, HEIGHT, TILE_SIZE) for _ in range(ORB_COUNT)]

icon = pygame.image.load(ICON_PATH)
pygame.display.set_icon(icon)

ga = GeneticAlgorithm(POPULATION_SIZE, INPUT_SIZE, HIDDEN_SIZE, OUTPUT_SIZE, WIDTH, HEIGHT, TILE_SIZE)

# Track best performance across all generations
all_time_best_fitness = 0
all_time_best_snake = None
all_time_best_generation = 0
fitness_history = []
generation_stats = []

print("Training Started")
print("="*60)

generation = 0
while generation < GENERATION_LIMIT:
    print(f"\nGeneration {generation + 1}/{GENERATION_LIMIT}")
    
    population = ga.get_population()
    
    for snake_idx, snake in enumerate(population):
        snake.reset()
        food = Food(WIDTH, HEIGHT, TILE_SIZE)
        steps = 0

        while snake.alive and steps < MAX_STEPS_PER_SNAKE:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if all_time_best_snake:
                        model_manager.save_best_model(all_time_best_snake)
                    pygame.quit()
                    sys.exit()

            snake.update(food)
            if food.collision(snake.head_pos()):
                snake.grow()
                food.reset()
           # visualize every 50th snake
            if snake_idx % 50 == 0: 
                screen.blit(background, (0, 0))
                
                #Draw background ambient orbs
                for orb in orbs:
                    orb.update()
                    orb.draw(screen)
                
                # Draw snake
                snake.draw(screen)
                
                # Draw food
                food.update()
                food.draw(screen)
                
                # Display info on screen
                info_lines = [
                    f"Generation: {generation + 1}/{GENERATION_LIMIT}",
                    f"Snake: {snake_idx + 1}/{POPULATION_SIZE}",
                    f"Steps: {steps}/{MAX_STEPS_PER_SNAKE}",
                    f"Current Fitness: {snake.fitness:.2f}",
                    f"Food Eaten: {snake.food_eaten}",
                    f"Body Length: {len(snake.body)}",
                    f"All-Time Best: {all_time_best_fitness:.2f}",
                    f"Best Gen: {all_time_best_generation}"
                ]
                
                for i, line in enumerate(info_lines):
                    text_surface = font.render(line, True, (255, 255, 255))
                    screen.blit(text_surface, (10, 10 + i * 24))
                
                pygame.display.flip()
                clock.tick(FPS)
            
            steps += 1
        
        # Evaluate final fitness
        snake.evaluate_final_fitness()
    
    # Calculate generation statistics
    fitnesses = [snake.fitness for snake in population]
    best_fitness = max(fitnesses)
    avg_fitness = np.mean(fitnesses)
    worst_fitness = min(fitnesses)
    std_fitness = np.std(fitnesses)
    best_snake = max(population, key=lambda s: s.fitness)
    
    # Print generation results
    print(f"   Best Fitness: {best_fitness:.2f}")
    print(f"   Avg Fitness: {avg_fitness:.2f}")
    
    # Check if this is the best snake ever
    if best_fitness > all_time_best_fitness:
        all_time_best_fitness = best_fitness
        all_time_best_snake = best_snake
        all_time_best_generation = generation + 1
        print(f"🐍 NEW RECORD Fitness: {best_fitness:.2f}")
        
        # Save the Best Model
        model_manager.save_best_model(best_snake)

        summary = {
            "best_fitness": round(best_fitness, 2),
            "generation": all_time_best_generation,
            "population_size": POPULATION_SIZE,
            "food_eaten": best_snake.food_eaten,
            "time_alive": best_snake.steps
        }

        # Save Model sumamry stats
        summary_path = os.path.join(MODEL_DIR, "training_summary.json")
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=4)
        print(f"📁 Summary updated at: {summary_path}")

        if best_fitness >= EARLY_STOP_FITNESS:
            print(f"\n EARLY STOP: {EARLY_STOP_FITNESS} fitness achieved.")
            break

    
    ga.create_next_generation()
    generation += 1

# Training complete
print("\n" + "="*60)
print("TRAINING COMPLETE!")
print("="*60)

# Save Best Snake Stats for Confirmation
final_best_snake = all_time_best_snake if all_time_best_snake else ga.get_best_snake()
final_fitness = all_time_best_fitness if all_time_best_snake else final_best_snake.fitness
final_generation = all_time_best_generation if all_time_best_snake else generation
