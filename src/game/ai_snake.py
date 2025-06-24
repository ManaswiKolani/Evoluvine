import pygame
from constants import *
from src.Brain.neural_network import NeuralNetwork
import math
import numpy as np
from collections import deque, Counter

class AISnake:
    def __init__(self, start_pos, tile_size, screen_width, screen_height, brain=None):
        # Config Attributes
        self.tile_size = tile_size
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.initial_pos = start_pos
        self.body = [start_pos]
        
        # Randomize start direction
        initial_directions = [(tile_size, 0), (-tile_size, 0), (0, tile_size), (0, -tile_size)]
        self.direction = initial_directions[np.random.randint(len(initial_directions))]
        
        # Snake Status Attributes
        self.grow_next = False
        self.alive = True
        
        # Default Brain Value
        self.brain = brain if brain else NeuralNetwork([4, 6, 3])

        # Fitness attributes
        self.fitness = 0.0 # snake fitness to calculate performance
        self.food_eaten = 0 # food eaten
        self.steps = 0 # number fo total steps taken
        self.idle_steps = 0 # steps taken without reward
        self.max_idle_steps = 150  # maximum idle steps without penalty
        
        # Distace attributes to evaluate fitness
        self.last_food_distance = float('inf')
        self.distance_improvements = 0
        
        # Maximum possible distance
        self.max_distance = math.sqrt(screen_width**2 + screen_height**2)
        
        # Exploration tracking
        self.visited_positions = set()
        self.exploration_bonus_given = set()
        self.last_direction_change = 0
        
        # Attributes to prevent idle loops
        self.recent_positions = deque(maxlen=20)  # last 20 positions
        self.position_counts = Counter()  # visiting frequency
        self.recent_directions = deque(maxlen=10)  # last 10 directions taken
        
        # Loop detection parameters
        self.loop_penalty_threshold = 5  # Penalty after visiting same position 3 times
        self.max_position_revisits = 8  # Maximum times to visit same position
        self.direction_repetition_threshold = 20  # Penalty for same direction too long
        
        # Circular movement detection
        self.movement_pattern_history = deque(maxlen=16)  # Track movement patterns
        self.last_loop_penalty_step = 0  # Prevent spam penalties
        
        # Load snake sprites
        self.image = pygame.image.load(SNAKE_LIVE_PATH).convert_alpha()
        self.image = pygame.transform.scale(self.image, (tile_size, tile_size))

        self.death_image = pygame.image.load(SNAKE_DEAD_PATH).convert_alpha()
        self.death_image = pygame.transform.scale(self.death_image, (tile_size, tile_size))

    def reset(self):
        """
        Reset snake to initial state
        
        """
        self.body = [self.initial_pos]
        
        # Select Random Initial Direction
        initial_directions = [(self.tile_size, 0), (-self.tile_size, 0), (0, self.tile_size), (0, -self.tile_size)]
        self.direction = initial_directions[np.random.randint(len(initial_directions))]
        
        # Reset all attributes of fitness
        self.grow_next = False
        self.alive = True
        self.fitness = 0.0
        self.food_eaten = 0
        self.steps = 0
        self.idle_steps = 0
        self.last_food_distance = float('inf')
        self.distance_improvements = 0
        self.visited_positions = set()
        self.exploration_bonus_given = set()
        self.last_direction_change = 0
        
        # Reset loop prevention tracking
        self.recent_positions.clear()
        self.position_counts.clear()
        self.recent_directions.clear()
        self.movement_pattern_history.clear()
        self.last_loop_penalty_step = 0

    def head_pos(self):
        return self.body[0]

    def get_relative_directions(self):
        dx, dy = self.direction
        # [forward, left, right]
        return [
            (dx, dy),           # forward
            (dy, -dx),          # left 
            (-dy, dx)           # right 
        ]


    def check_danger_in_direction(self, direction):
        head = self.head_pos()
        next_pos = (head[0] + direction[0], head[1] + direction[1])
        
        # Check walls
        if (next_pos[0] < 0 or next_pos[0] >= self.screen_width or
            next_pos[1] < 0 or next_pos[1] >= self.screen_height):
            return True
        
        # Check self collision
        if next_pos in self.body:
            return True
        
        return False

    def get_food_angle(self, food_pos):
        head = self.head_pos()
        
        # Current direction vector (normalized)
        curr_dir = np.array(self.direction, dtype=float)
        curr_dir = curr_dir / np.linalg.norm(curr_dir)
        
        # Food direction vector
        food_vec = np.array([food_pos[0] - head[0], food_pos[1] - head[1]], dtype=float)
        # return 0, if collision
        if np.linalg.norm(food_vec) == 0:
            return 0.0
        # Normalize food vector
        food_vec = food_vec / np.linalg.norm(food_vec)

        # Calculate sine of angle
        sin_angle = curr_dir[0] * food_vec[1] - curr_dir[1] * food_vec[0]
        return sin_angle

    def get_sensor_inputs(self, food):
        directions = self.get_relative_directions()
        
        # Get Input Values
        forward_danger = 1.0 if self.check_danger_in_direction(directions[0]) else 0.0
        left_danger = 1.0 if self.check_danger_in_direction(directions[1]) else 0.0
        right_danger = 1.0 if self.check_danger_in_direction(directions[2]) else 0.0
        food_angle = self.get_food_angle(food.position)
        
        inputs = [forward_danger, left_danger, right_danger, food_angle]
        
        return np.array(inputs, dtype=np.float32)

    def detect_circular_pattern(self):
        if len(self.movement_pattern_history) < 8:
            return False
        
        # Convert recent movements to a pattern string
        pattern = list(self.movement_pattern_history)
        pattern_len = len(pattern)
        
        # check for repeatign patterns:
        # line, triangle and rectangular patterns
        for cycle_len in [2, 3, 4]:
            if pattern_len >= cycle_len * 2:
                first_cycle = pattern[-cycle_len*2:-cycle_len]
                second_cycle = pattern[-cycle_len:]
                
                if first_cycle == second_cycle:
                    return True
        
        return False

    def detect_back_and_forth(self):
        if len(self.recent_directions) < 6:
            return False
        
        directions = list(self.recent_directions)
        
        opposite_pairs = 0
        for i in range(len(directions) - 1):
            curr_dir = directions[i]
            next_dir = directions[i + 1]
            
            if (curr_dir[0] == -next_dir[0] and curr_dir[1] == -next_dir[1]):
                opposite_pairs += 1
        
        return opposite_pairs >= 3

    def calculate_repetition_penalty(self):
        penalty = 0.0
        if self.steps - self.last_loop_penalty_step < 5:
            return penalty

        current_pos = self.head_pos()
        position_visits = self.position_counts.get(current_pos, 0)
        
        # Position revisit penalty
        if position_visits >= self.loop_penalty_threshold:
            penalty += (position_visits - self.loop_penalty_threshold + 1) ** 2 * 2.0
        
        # Same direction penalty
        if len(self.recent_directions) >= self.direction_repetition_threshold:
            if all(d == list(self.recent_directions)[0] for d in list(self.recent_directions)[-self.direction_repetition_threshold:]):
                penalty += 8.0
        
        # Pattern penalties
        if self.detect_circular_pattern():
            penalty += 15.0
            self.last_loop_penalty_step = self.steps
        
        if self.detect_back_and_forth():
            penalty += 10.0
            self.last_loop_penalty_step = self.steps
        
        # Bounded Exploration Penatly:
        if len(self.recent_positions) >= 15:
            positions = list(self.recent_positions)
            x_range = max(pos[0] for pos in positions) - min(pos[0] for pos in positions)
            y_range = max(pos[1] for pos in positions) - min(pos[1] for pos in positions)
            
            if x_range <= self.tile_size * 4 and y_range <= self.tile_size * 4:
                penalty += 5.0
        
        # Kill if stuck in a loop
        if position_visits >= self.max_position_revisits:
            penalty += 25.0
            if position_visits >= 8:
                self.die("stuck in loop")
        
        return penalty

    def make_decision(self, inputs):
        if not self.alive:
            return
        
        old_direction = self.direction
        
        output = self.brain.feedforward(inputs)
        action = np.argmax(output)
        
        directions = self.get_relative_directions()
        chosen_direction = directions[action]
        
        self.direction = chosen_direction
        
        if old_direction != chosen_direction:
            self.last_direction_change = self.steps
        
        # Update patterns for loop detection
        movement_code = self.direction_to_code(chosen_direction)
        self.movement_pattern_history.append(movement_code)
        self.recent_directions.append(chosen_direction)

    def direction_to_code(self, direction):
        dx, dy = direction
        if dx > 0:
            return 'R'  # Right
        elif dx < 0:
            return 'L'  # Left
        elif dy > 0:
            return 'D'  # Down
        else:
            return 'U'  # Up

    def move(self):
        if not self.alive:
            return
        
        # Calculate new head position
        new_head = (self.body[0][0] + self.direction[0],
                    self.body[0][1] + self.direction[1])
        
        # Check wall collision
        if (new_head[0] < 0 or new_head[0] >= self.screen_width or
            new_head[1] < 0 or new_head[1] >= self.screen_height):
            self.die("wall collision")
            return
        
        # Check self collision
        if new_head in self.body:
            self.die("self collision")
            return
        
        # Update position for loop detection
        self.recent_positions.append(new_head)
        self.position_counts[new_head] += 1
        
        # Move snake
        self.body.insert(0, new_head)
        if self.grow_next:
            self.grow_next = False
        else:
            self.body.pop()
        
        self.steps += 1

    def grow(self):
        self.grow_next = True
        self.food_eaten += 1
        self.idle_steps = 0  # Reset idle steps counter
        
        # Clear old loop detection history when food is eaten
        if len(self.recent_positions) > 10:
            positions_to_keep = list(self.recent_positions)[-10:]
            self.recent_positions.clear()
            self.recent_positions.extend(positions_to_keep)
        
        # Decrease position counts after successful food collection
        for pos in list(self.position_counts.keys()):
            self.position_counts[pos] = max(0, self.position_counts[pos] - 1)

    def die(self, reason="unknown"):
        self.alive = False

    def calculate_distance_to_food(self, food_pos):
        head = self.head_pos()
        return abs(head[0] - food_pos[0]) + abs(head[1] - food_pos[1])

    def get_normalized_distance(self, distance):
        return min(distance / self.max_distance, 1.0)

    def calculate_distance_fitness_change(self, current_distance, previous_distance):
        #initial fitness
        if previous_distance == float('inf'):
            normalized_distance = self.get_normalized_distance(current_distance)
            return (1.0 - normalized_distance) * 3.0 
        
        distance_change = previous_distance - current_distance
        
        #if closer
        if distance_change > 0:  
            normalized_change = distance_change / self.tile_size
            reward = normalized_change * 8.0 
            return reward
        elif distance_change < 0:  # if farther
            normalized_change = abs(distance_change) / self.tile_size
            penalty = -normalized_change * 1.5  # Less penality if movign away
            return penalty
        else:  
            # No change in distance:
            return -0.05

    def update_fitness(self, food):
        if not self.alive:
            return
        
        # Base survival + distance-based fitness
        self.fitness += 0.1
        current_distance = self.calculate_distance_to_food(food.position)
        self.fitness += self.calculate_distance_fitness_change(current_distance, self.last_food_distance)
        self.fitness -= self.calculate_repetition_penalty()
        
        # Exploration bonus
        current_pos = self.head_pos()
        exploration_zone = (current_pos[0] // (self.tile_size * 3), current_pos[1] // (self.tile_size * 3))
        if exploration_zone not in self.exploration_bonus_given:
            self.fitness += 5.0
            self.exploration_bonus_given.add(exploration_zone)
        
        # Direction change bonus
        if (self.steps > 10 and (self.steps - self.last_direction_change) < 3 and 
            len(self.recent_directions) >= 3):
            recent_dirs = list(self.recent_directions)[-3:]
            if not all(d == recent_dirs[0] for d in recent_dirs):
                self.fitness += 1.0
        
        # Update tracking variables
        if current_distance < self.last_food_distance:
            self.distance_improvements += 1
            self.idle_steps = 0
        else:
            self.idle_steps += 1
        self.last_food_distance = current_distance
        
        # Proximity bonus + idle penalties
        self.fitness += (1.0 - self.get_normalized_distance(current_distance)) * 0.15
        
        if self.idle_steps > 30 and self.steps > 50:
            self.fitness -= (self.idle_steps - 30) * 0.05
        
        if self.idle_steps > self.max_idle_steps:
            self.fitness -= 30
            self.die("idle timeout")

    def evaluate_final_fitness(self):
        # Large food bonus
        food_bonus = self.food_eaten * 100
        
        # small survival bonus
        survival_bonus = self.steps * 0.05
        
        # Growth bonus
        length_bonus = len(self.body) * 20
        
        # Distance bonus
        efficiency_bonus = self.distance_improvements * 3
        
        # Death penalty
        death_penalty = 0 if self.alive else -25
        
        # Loop penalty
        total_revisits = sum(max(0, count - 1) for count in self.position_counts.values())
        loop_penalty = total_revisits * 0.5  # extra visit
        
        # Total Fitness Calculation
        final_fitness = (self.fitness + food_bonus + survival_bonus + 
                        length_bonus + efficiency_bonus + death_penalty - loop_penalty)
        
        # Non Negavtive Fitness
        self.fitness = max(0, final_fitness)
        
        return self.fitness

    def update(self, food):
        """Update snake for one step"""
        if not self.alive:
            return
            
        inputs = self.get_sensor_inputs(food)
        
        self.make_decision(inputs)
        self.move()
        self.update_fitness(food)

    def draw(self, surface):
        for i, segment in enumerate(self.body):
            if self.alive:
                surface.blit(self.image, segment)
            else:
                surface.blit(self.death_image, segment)

    def get_loop_stats(self):
        """Get statistics for debugging"""
        return {
            'position_revisits': dict(self.position_counts),
            'max_revisits': max(self.position_counts.values()) if self.position_counts else 0,
            'unique_positions': len(self.position_counts),
            'recent_pattern': ''.join(list(self.movement_pattern_history)[-8:]) if self.movement_pattern_history else '',
            'circular_detected': self.detect_circular_pattern(),
            'back_forth_detected': self.detect_back_and_forth()
        }