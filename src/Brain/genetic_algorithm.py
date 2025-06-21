import random
from game.ai_snake import AISnake
from Brain.neural_network import NeuralNetwork

class GeneticAlgorithm:
    def __init__(self, population_size, input_size, hidden_layers, output_size,
                 screen_width, screen_height, tile_size):
        self.population_size = population_size
        self.input_size = input_size
        self.hidden_layers = hidden_layers
        self.output_size = output_size
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.tile_size = tile_size

        self.population = self.create_initial_population()

    def create_initial_population(self):
        layers = [self.input_size] + self.hidden_layers + [self.output_size]
        initial_population = [AISnake(start_pos=(self.screen_width // 2, self.screen_height // 2),
                                     tile_size=self.tile_size, screen_width=self.screen_width,
                                     screen_height=self.screen_height, brain=NeuralNetwork(layers))
                                     
                                     for _ in range(self.population_size)]
        
        return initial_population
    
    def evaluate_fitness(self):
        return sorted(self.population, key=lambda snake: snake.fitness, reverse=True)
    

    def next_generation(self, retain_best = 0.2, mutation_rate=0.1, mutation_strength=0.2):
        sorted_population = self.evaluate_fitness()
        retain_length = int(self.population_size * retain_best)

        next_gen = []
        for i in range(retain_length):
            brain_copy = sorted_population[i].brain.copy()
            next_gen.append(self._create_snake_with_brain(brain_copy))

        while len(next_gen) < self.population_size:
            parent = random.choice(sorted_population[:retain_length])
            mutated_brain = parent.brain.copy()
            mutated_brain.mutate(mutation_rate, mutation_strength)
            next_gen.append(self._create_snake_with_brain(mutated_brain))

        self.population = next_gen

    def _create_snake_with_brain(self, brain):
        return AISnake(start_pos=(self.screen_width // 2, self.screen_height // 2),
                       tile_size=self.tile_size, screen_width=self.screen_width,
                       screen_height=self.screen_height, brain=brain)
    
    def get_population(self):
        return self.population
    

        
       