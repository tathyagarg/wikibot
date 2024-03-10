import numpy as np
import utils

DAMPING = utils.PROJECT.QUERY_ANALYZER['DAMPING']
ALPHA = utils.PROJECT.QUERY_ANALYZER['ALPHA']
LAMBDA = utils.PROJECT.QUERY_ANALYZER['LAMBDA']
EPOCHS = utils.PROJECT.QUERY_ANALYZER['EPOCHS']

class RecurrentNN:
    def __init__(self, input_state, input_size, hidden_size, output_size, truth, activation=None, activation_deriv=None, output_activation=None) -> None:
        self.input_state = input_state
        if activation_deriv and not activation or activation and not activation_deriv:
            raise KeyError("Must include both activation and activation_deriv")
        
        self.activation = activation or np.tanh
        self.activation_derivative = activation_deriv or (lambda v: 1/np.cosh(v)**2) # d(tanhx)/dx = sech^2(x)
        self.output_activation = output_activation or (lambda v: np.round(100 * v))
        
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

        self.truth = truth / 100

    def forward_pass(self):
        self.hidden_state = self.activation(np.dot(self.input_state, self.weights[0]) + np.dot(self.hidden_state, self.weights[1]) + self.biases[0])
        self.output_state = self.activation(np.dot(self.hidden_state, self.weights[2]) + np.dot(self.output_state, self.weights[3]) + self.biases[1]) 

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

                z = np.dot(x, W) + b
                h = self.activation(z)
                y_hat = (np.dot(h, U) + c)

                dL_dy_hat = 2 * (y_hat - y)

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

    def loss(self):
        mse_loss = (self.output_state[0] - self.truth) ** 2
        W, U, b, c = self.weights[0], self.weights[2], self.biases[0], self.biases[1]

        regularization_loss = 0.5 * LAMBDA * (np.sum(W**2) + np.sum(U**2) + np.sum(b**2) + np.sum(c**2))

        return mse_loss + regularization_loss
    
    @property
    def activated_output(self):
        return self.output_activation(self.output_state)
