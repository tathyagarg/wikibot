import numpy as np
import utils as utils
import math

DAMPING = utils.PROJECT.QUERY_ANALYZER['DAMPING']
ALPHA = utils.PROJECT.QUERY_ANALYZER['ALPHA']
EPOCHS = utils.PROJECT.QUERY_ANALYZER['EPOCHS']

def magnitude(value):
    return math.floor(np.log10(value))

class RecurrentNeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size, *, activation=None, activation_deriv=None, output_activation=None) -> None:
        self._input_state = []

        if activation_deriv and not activation or activation and not activation_deriv:
            raise KeyError("Must include both activation and activation_deriv")
        
        self._truth = float('inf')
        self.truth_magnitude = -1

        self.activation = activation or np.tanh
        self.activation_derivative = activation_deriv or (lambda v: 1/np.cosh(v)**2) # d(tanhx)/dx = sech^2(x)
        self.output_activation = output_activation or (lambda v: np.round((10 ** self.truth_magnitude) * v))
        
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

        self.weights = [
            np.random.randn(input_size, hidden_size) * DAMPING,  # Input -> hidden
            np.random.randn(hidden_size, hidden_size) * DAMPING, # Hidden -> hidden
            np.random.randn(hidden_size, output_size) * DAMPING, # Hidden -> output
        ]

        self.biases = [
            np.zeros(hidden_size),
            np.zeros(output_size)
        ]

        self.hidden_state = None
        self.output_state = None

    def set_properties(self, input_state, truth):
        self.input_state = input_state
        self.truth = truth

        self.hidden_state = self.activation(np.dot(self.input_state, self.weights[0]) + self.biases[0])
        self.output_state = self.activation(np.dot(self.hidden_state, self.weights[2]) + self.biases[1])


    @property
    def input_state(self):
        return self._input_state
    
    @input_state.setter
    def input_state(self, value):
        self._input_state = value

    @property
    def truth(self):
        return self._truth
    
    @truth.setter
    def truth(self, value):
        if value == 0:
            self.truth_magnitude = 1
        else:
            self.truth_magnitude = magnitude(value) + 1
        self._truth = value / (10 ** self.truth_magnitude)

    def forward_pass(self):
        self.hidden_state = self.activation(np.dot(self.input_state, self.weights[0]) + np.dot(self.hidden_state, self.weights[1]) + self.biases[0])
        self.output_state = self.activation(np.dot(self.hidden_state, self.weights[2]) + self.biases[1]) 

    def backward_passes(self, *, inputs=None, epochs=5):
        dL_dW = np.zeros_like(self.weights[0])
        dL_dU = np.zeros_like(self.weights[2])
        dL_db = np.zeros_like(self.biases[0])
        dL_dc = np.zeros_like(self.biases[1])

        inputs = inputs or [(self.input_state, self.truth)]

        for _ in range(epochs):
            for x, y in inputs:
                x = x
                y = y
                W = self.weights[0]
                U = self.weights[2]
                b = self.biases[0]
                c = self.biases[1]

                z = np.dot(np.dot(x, W) + b, self.weights[1])
                h = self.activation(z)
                y_hat = self.activation(np.dot(h, U) + c)

                dL_dy_hat = 4 * (y_hat - y)

                dL_dW += (dL_dy_hat * U * x  * self.activation_derivative(z).reshape((self.hidden_size,self.output_size))).reshape((self.input_size, self.hidden_size))
                dL_dU += (dL_dy_hat * h).reshape((self.hidden_size, self.output_size))
                dL_db += (self.activation_derivative(z).reshape((self.hidden_size, self.output_size)) * dL_dy_hat * U).reshape((self.hidden_size))
                dL_dc += (dL_dy_hat)
        
        dL_dW /= len(inputs)*epochs
        dL_dU /= len(inputs)*epochs
        dL_db /= len(inputs)*epochs
        dL_dc /= len(inputs)*epochs

        self.weights[0] -= ALPHA * dL_dW
        self.weights[2] -= ALPHA * dL_dU
        self.biases[0]  -= ALPHA * dL_db
        self.biases[1]  -= ALPHA * dL_dc
    
    @property
    def activated_output(self):
        return self.output_activation(self.output_state)

    def train(self, epochs=None):
        epochs = epochs or EPOCHS
        for _ in range(epochs):
            self.forward_pass()
            self.backward_passes()
            print(f"{_} {self.activated_output=} {self.output_state}")