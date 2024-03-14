import numpy as np
import utils
import math
import data

DAMPING = utils.PROJECT.QUERY_ANALYZER['DAMPING']
ALPHA = utils.PROJECT.QUERY_ANALYZER['ALPHA']
EPOCHS = utils.PROJECT.QUERY_ANALYZER['EPOCHS']

def magnitude(value):
    return math.floor(np.log10(value))

class RecurrentNeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size, *, activation=None, activation_deriv=None, output_activation=None) -> None:
        self.input_state = []

        if activation_deriv and not activation or activation and not activation_deriv:
            raise KeyError("Must include both activation and activation_deriv")
        
        self._truth = float('inf')
        self.truth_magnitude = 1

        self.activation = activation or np.tanh
        self.activation_derivative = activation_deriv or (lambda v: 1/np.cosh(v)**2) # d(tanhx)/dx = sech^2(x)
        self.output_activation = output_activation or (lambda v, t: np.round((10 ** t) * v))
        
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

        self.W = np.random.randn(input_size, hidden_size) * DAMPING,  # Input -> hidden
        self.V = np.random.randn(hidden_size, hidden_size) * DAMPING, # Hidden -> hidden
        self.U = np.random.randn(hidden_size, output_size) * DAMPING, # Hidden -> output


        self.b = np.random.randn(hidden_size)
        self.c = np.random.randn(output_size)

        self.hidden_state = None
        self.output_state = None

    def set_properties(self, input_state, truth):
        self.input_state = input_state
        self.truth = truth

        self.hidden_state = self.activation(np.dot(self.input_state, self.W) + self.b)
        self.output_state = self.activation(np.dot(self.hidden_state, self.U) + self.c)

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

    def backward_passes(self, *, inputs=None, epochs=5):
        inputs = inputs or [(self.input_state, self.truth)]

        for _ in range(epochs):
            dW = np.zeros_like(self.W)
            dU = np.zeros_like(self.U)
            db = np.zeros_like(self.b)
            dc = np.zeros_like(self.c)

            W = self.W
            U = self.U
            b = self.b
            c = self.c
            length = len(inputs)

            for x, y in inputs:
                z = np.dot(x, W) + b
                h = self.activation(z)
                y_hat = self.output_activation(np.dot(h, U) + c, 1)

                dY = 2 * (y_hat - y)  # This is equal to \frac{\partial{(y - \hat{y})^2}}{\partial{\theta}} / \frac{\partial{(y - \hat(y))}}{\partial{\theta}} (in LaTeX)

                dW += (dY * U * self.activation_derivative(z).reshape((self.hidden_size, self.output_size)) * x).reshape((self.input_size, self.hidden_size))
                dU += (dY * z).reshape((self.hidden_size, self.output_size))
                db += (dY * self.activation_derivative(z).reshape((self.hidden_size, self.output_size)) * U).reshape((self.hidden_size))
                dc += dY.reshape((self.output_size))

            self.W -= ALPHA * (dW / length)
            self.U -= ALPHA * (dU / length)
            self.b -= ALPHA * (db / length)
            self.c -= ALPHA * (dc / length)
    
    @property
    def activated_output(self):
        self.forward_pass()
        return self.output_activation(self.output_state)

    def train_on(self, dataset, *, epochs=EPOCHS, min_time=1.5, bar_length=100):
        for _ in utils.Bar(range(epochs), min_time=min_time, length=bar_length):
            self.backward_passes(inputs=dataset)

    def forward_pass(self):
        if self.hidden_state == None:
            self.hidden_state = np.dot(self.input_state, self.W) + self.b
            self.output_state = np.dot(self.activation(self.hidden_state), self.U) + self.c
        else:
            self.hidden_state = np.dot(self.input_state, self.W) + np.dot(self.hidden_state, self.V) + self.b
            self.output_state = np.dot(self.activation(self.hidden_state), self.U) + self.c

    def predict(self, inputs):
        self.input_state = inputs
        self.hidden_state = None
        self.forward_pass()
        return self.output_activation(self.output_state, 1)
