import pickle
import os
import numpy as np
from src.constants import *
from src.Brain.neural_network import NeuralNetwork
from src.game.ai_snake import AISnake

class ModelManager:
    def __init__(self, model_dir=MODEL_DIR):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
    
    def save_best_model(self, snake):
        try:
            model_data = {
                'brain': {
                    'layers': snake.brain.layers,
                    'weights': [w.tolist() for w in snake.brain.weights],
                    'biases': [b.tolist() for b in snake.brain.biases]
                }
            }
            pickle_path = os.path.join(self.model_dir, 'best_model.pkl')
            with open(pickle_path, 'wb') as f:
                pickle.dump(model_data, f)
            return True
            
        except Exception as e:
            print(f"Error saving model: {e}")
            return False
    
    def load_best_model(self, file_path=None):
        if file_path is None:
            file_path = MODEL_PATH
        
        try:
            with open(file_path, 'rb') as f:
                model_data = pickle.load(f)
            
            model_data['brain']['weights'] = [np.array(w) for w in model_data['brain']['weights']]
            model_data['brain']['biases'] = [np.array(b) for b in model_data['brain']['biases']]
            
            return model_data
            
        except FileNotFoundError:
            print(f"Model file not found: {file_path}")
            return None
        except Exception as e:
            print(f"Error loading model: {e}")
            return None
    
    def create_snake_from_model(self, model_data, screen_width, screen_height, tile_size):
        try:
            brain = NeuralNetwork(model_data['brain']['layers'])
            
            brain.load_weights(
                model_data['brain']['weights'],
                model_data['brain']['biases']
            )
        
            snake = AISnake(
                start_pos=(screen_width // 2, screen_height // 2),
                tile_size=tile_size,
                screen_width=screen_width,
                screen_height=screen_height,
                brain=brain
            )
            
            return snake
            
        except Exception as e:
            print(f"Error creating snake from model: {e}")
            return None