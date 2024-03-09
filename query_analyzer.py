import numpy as np

DAMPING = 1/10
ALPHA = 1

class RecurrentNN:
    def __init__(self, input_state, input_size, hidden_size, output_size, truth, activation=None, activation_deriv=None) -> None:
        self.input_state = input_state
        if activation_deriv and not activation or activation and not activation_deriv:
            raise KeyError("Must include both activation and activation_deriv")
        
        self.activation = activation or np.tanh
        self.activation_derivative = activation_deriv or (lambda v: 1 - (np.tanh(v)**2))
        
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

        self.weights = [
            np.random.randn(input_size, hidden_size) * DAMPING,  # Input -> hidden
            np.random.randn(hidden_size, hidden_size) * DAMPING, # Hidden -> hidden
            np.random.randn(hidden_size, output_size) * DAMPING, # Hidden -> output
            np.random.randn(output_size) * DAMPING               # Output -> [x]
        ]

        self.biases = [
            np.zeros(hidden_size),
            np.zeros(output_size)
        ]

        self.hidden_state = self.activation(np.dot(self.input_state, self.weights[0]) + self.biases[0])
        self.output_state = self.activation(np.dot(self.hidden_state, self.weights[2]) + self.biases[1])

        self.truth = truth

    def forward_pass(self):
        self.hidden_state = self.activation(np.dot(self.input_state, self.weights[0]) + np.dot(self.hidden_state, self.weights[1]) + self.biases[0])
        self.output_state = self.activation(np.dot(self.hidden_state, self.weights[2]) + np.dot(self.output_state, self.weights[3]) + self.biases[1])

    def backward_pass(self):
        z = np.dot(self.input_state, self.weights[0]) + self.biases[0]
        h = np.tanh(z)
        y_hat = np.dot(h, self.weights[2]) + self.biases[1]

        dL_dy_hat = 2 * (y_hat - self.truth)

        dL_dW = (dL_dy_hat * self.weights[2] * self.input_state).reshape((3, 4))
        dL_dU = (dL_dy_hat * z).reshape((4, 1))
        dL_db = (dL_dy_hat * self.weights[2]).reshape((4))
        dL_dc = (dL_dy_hat)

        self.weights[0] -= ALPHA * dL_dW
        self.weights[2] -= ALPHA * dL_dU
        self.biases[0]  -= ALPHA * dL_db
        self.biases[1]  -= ALPHA * dL_dc

    def loss(self):
        return RecurrentNN.calculate_loss(self.truth, self.output_state[0])
    
    @classmethod
    def calculate_loss(cls, y, y_hat):
        return (y_hat-y)**2

