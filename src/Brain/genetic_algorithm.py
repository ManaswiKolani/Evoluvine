"""
Filename: genetic_algorithm.py
Author: Manaswi Kolani
Description: This module implements the population, crossover, mutation, selectiona and diversity for the genetic algorithm
"""
import numpy as np
from src.Brain.neural_network import NeuralNetwork
from src.game.ai_snake import AISnake

class GeneticAlgorithm:
    def __init__(self, population_size, input_size, hidden_size, output_size, screen_width, screen_height, tile_size):
        self.population_size = population_size
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.tile_size = tile_size
        self.population = self._initialize_population()
        self.generation = 0
        self.elitism_rate = 0.1

    def _initialize_population(self):
        layers = [self.input_size, self.hidden_size, self.output_size]
        population = []
        
        for _ in range(self.population_size):
            snake = AISnake(
                start_pos=(self.screen_width // 2, self.screen_height // 2),
                tile_size=self.tile_size,
                screen_width=self.screen_width,
                screen_height=self.screen_height,
                brain=NeuralNetwork(layers)
            )
            self._xavier_initialization(snake.brain)
            population.append(snake)
        
        return population

    def _xavier_initialization(self, brain):
        for i, (prev_size, curr_size) in enumerate(zip(brain.layers[:-1], brain.layers[1:])):
            limit = np.sqrt(6 / (prev_size + curr_size))
            brain.weights[i] = np.random.uniform(-limit, limit, brain.weights[i].shape)
            brain.biases[i] = np.random.uniform(-limit, limit, brain.biases[i].shape)

    def fitness_sharing(self, population):
        sigma_share = 1.0 
        
        for i, snake in enumerate(population):
            niche_count = 0
            for j, other_snake in enumerate(population):
                if i != j:
                    distance = self._calculate_genetic_distance(snake, other_snake)
                    if distance < sigma_share:
                        sharing_value = 1 - (distance / sigma_share)
                        niche_count += sharing_value
            
            if niche_count > 0:
                snake.shared_fitness = snake.fitness / (1 + niche_count)
            else:
                snake.shared_fitness = snake.fitness

    def _calculate_genetic_distance(self, snake1, snake2):
        total_distance = 0
        total_elements = 0
        
        for w1, w2 in zip(snake1.brain.weights, snake2.brain.weights):
            distance = np.sum((w1 - w2) ** 2)
            total_distance += distance
            total_elements += w1.size
        
        for b1, b2 in zip(snake1.brain.biases, snake2.brain.biases):
            distance = np.sum((b1 - b2) ** 2)
            total_distance += distance
            total_elements += b1.size
        
        return np.sqrt(total_distance / total_elements)

    def roulette_wheel_selection(self, population):
        fitnesses = [getattr(snake, 'shared_fitness', snake.fitness) for snake in population]
        min_fitness = min(fitnesses)
        adjusted_fitnesses = [f - min_fitness + 1 for f in fitnesses]
        
        total_fitness = sum(adjusted_fitnesses)
        if total_fitness == 0:
            return np.random.choice(population)
        
        probabilities = [f / total_fitness for f in adjusted_fitnesses]
        return np.random.choice(population, p=probabilities)

    def two_point_roulette_selection(self, population):
        parent1 = self.roulette_wheel_selection(population)
        parent2 = self.roulette_wheel_selection(population)
        
        # Select different parents
        while parent2 is parent1 and len(population) > 1:
            parent2 = self.roulette_wheel_selection(population)
            
        return parent1, parent2

    def arithmetic_crossover(self, parent1, parent2, alpha=0.5):
        child_brain = NeuralNetwork(parent1.brain.layers)
        
        # Arithmetic crossover for weights 
        for i in range(len(parent1.brain.weights)):
            child_brain.weights[i] = (alpha * parent1.brain.weights[i] + 
                                    (1 - alpha) * parent2.brain.weights[i])
        
        # Arithmetic crossover for biases
        for i in range(len(parent1.brain.biases)):
            child_brain.biases[i] = (alpha * parent1.brain.biases[i] + 
                                   (1 - alpha) * parent2.brain.biases[i])
        
        return AISnake(
            start_pos=(self.screen_width // 2, self.screen_height // 2),
            tile_size=self.tile_size,
            screen_width=self.screen_width,
            screen_height=self.screen_height,
            brain=child_brain
        )

    def whole_mutation(self, snake, mutation_rate=0.3):
        for i in range(len(snake.brain.weights)):
            mutation_mask = np.random.random(snake.brain.weights[i].shape) < mutation_rate
            new_values = np.random.uniform(-1, 1, snake.brain.weights[i].shape)
            snake.brain.weights[i] = np.where(mutation_mask, new_values, snake.brain.weights[i])
        
        for i in range(len(snake.brain.biases)):
            mutation_mask = np.random.random(snake.brain.biases[i].shape) < mutation_rate
            new_values = np.random.uniform(-1, 1, snake.brain.biases[i].shape)
            snake.brain.biases[i] = np.where(mutation_mask, new_values, snake.brain.biases[i])

    def create_next_generation(self):
       
        # Evaluate fitness for all snakes
        for snake in self.population:
            snake.evaluate_final_fitness()
        
        self.fitness_sharing(self.population)
        
        # Sort population by original fitness
        sorted_population = sorted(self.population, key=lambda snake: snake.fitness, reverse=True)
        
        next_generation = []
        
        # Elitism: Keep top performers unchanged
        elite_count = int(self.population_size * self.elitism_rate)
        next_generation.extend(sorted_population[:elite_count])
        
        # Create rest of population through crossover and mutation
        while len(next_generation) < self.population_size:
            parent1, parent2 = self.two_point_roulette_selection(sorted_population)
            
            child = self.arithmetic_crossover(parent1, parent2)
            
            self.whole_mutation(child, mutation_rate=0.3)
            
            next_generation.append(child)
        
        self.population = next_generation
        self.generation += 1
        
        # Print stats
        best_fitness = sorted_population[0].fitness
        avg_fitness = np.mean([snake.fitness for snake in sorted_population])
        print(f"Generation {self.generation}: Best={best_fitness:.2f}, Avg={avg_fitness:.2f}")

    def get_population(self):
        return self.population

    def get_best_snake(self):
        return max(self.population, key=lambda snake: snake.fitness)

    def get_generation_stats(self):
        fitnesses = [snake.fitness for snake in self.population]
        return {
            'generation': self.generation,
            'best_fitness': max(fitnesses),
            'avg_fitness': np.mean(fitnesses),
            'worst_fitness': min(fitnesses),
            'std_fitness': np.std(fitnesses)
        }