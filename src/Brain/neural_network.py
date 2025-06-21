import numpy as np
import copy
import random


class NeuralNetwork:
    def __init__(self, layers):
        self.layers = layers
        self.weights = []
        self.biases = []


        # Initialize weights and biases
        for i in range(len(layers)-1):
            weight = np.random.randn(layers[i+1], layers[i])
            bias = np.random.randn(layers[i+1], 1)
            self.weights.append(weight)
            self.biases.append(bias)

    def feedforward(self, x):
        a = x.reshape(-1, 1)

        for i in range(len(self.weights) - 1):
            z = np.dot(self.weights[i], a) + self.biases[i]
            a = self.relu(z)

        # Last layer (no activation)
        z = np.dot(self.weights[-1], a) + self.biases[-1]
        return z.flatten()
    

    def relu (self, z):
        return np.maximum(0, z)
    
    def copy(self):
        new_nn = NeuralNetwork(self.layers)
        new_nn.weights = [w.copy() for w in self.weights]
        new_nn.biases = [b.copy() for b in self.biases]
        return new_nn
    
    def mutate(self, mutation_rate=0.2, mutation_strength=0.5):
        for i in range(len(self.weights)):
            mutation_mask = np.random.rand(*self.weights[i].shape) < mutation_rate
            self.weights[i] += mutation_mask * (np.random.randn(*self.weights[i].shape) * mutation_strength)

            mutation_mask = np.random.rand(*self.biases[i].shape) < mutation_rate
            self.biases[i] += mutation_mask * (np.random.randn(*self.biases[i].shape) * mutation_strength)

    