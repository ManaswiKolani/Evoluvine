
import numpy as np

class NeuralNetwork:
    
    def __init__(self, layers):
        self.layers = layers
        self.weights = []
        self.biases = []
        self.initialize_weights_and_biases()

    
    def initialize_weights_and_biases(self):
        for i in range(len(self.layers) - 1):
            # Initialize weights and biases for each layer with random values between -1 and 1
            weight = np.random.uniform(-1, 1, (self.layers[i + 1], self.layers[i]))
            bias = np.random.uniform(-1, 1, (self.layers[i + 1], 1))
            
            self.weights.append(weight)
            self.biases.append(bias)

   
    def sigmoid(self, x):
        x = np.clip(x, -500, 500) # Avoid overflow
        return 1 / (1 + np.exp(-x))


    def feedforward(self, x):
        if x.ndim == 1:
            x = x.reshape(-1, 1)

        for i in range(len(self.layers) - 1):
            z = np.dot(self.weights[i], x) + self.biases[i]
            x = self.sigmoid(z)

        return x.flatten()


    def copy(self):
        clone = NeuralNetwork(self.layers)
        clone.weights = [w.copy() for w in self.weights]
        clone.biases = [b.copy() for b in self.biases]
        return clone


    def get_total_parameters(self):
        total = 0
        for w, b in zip(self.weights, self.biases):
            total += w.size + b.size
        return total

    def get_network_summary(self):
        summary = {
            'layers': self.layers,
            'total_parameters': self.get_total_parameters(),
            'weights_shapes': [w.shape for w in self.weights],
            'biases_shapes': [b.shape for b in self.biases]
        }
        return summary

    def load_weights(self, weights, biases):
        if len(weights) != len(self.weights) or len(biases) != len(self.biases):
            raise ValueError("Error: Loading external weights and biases.")
        
        self.weights = [w.copy() for w in weights]
        self.biases = [b.copy() for b in biases]


    def save_weights(self):
        return {
            'weights': [w.copy() for w in self.weights],
            'biases': [b.copy() for b in self.biases],
            'layers': self.layers.copy()
        }