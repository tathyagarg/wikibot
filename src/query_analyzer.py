import numpy as np
import utils
import math
import data

analyzer_env = utils.PROJECT.QUERY_ANALYZER

DAMPING = analyzer_env['DAMPING']
ALPHA = analyzer_env['ALPHA']
EPOCHS = analyzer_env['EPOCHS']
TESTING_THRESHOLD = analyzer_env['TESTING_THRESHOLD']

def magnitude(value):
    return math.floor(np.log10(value))

class RecurrentNeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size, *, activation=None, activation_deriv=None, output_activation=None) -> None:
        self.input_state = []

        if activation_deriv and not activation or activation and not activation_deriv:
            raise KeyError("Must include both activation and activation_deriv")

        self.activation = activation or np.tanh
        self.activation_derivative = activation_deriv or (lambda v: 1/np.cosh(v)**2) # d(tanhx)/dx = sech^2(x)
        self.output_activation = output_activation or (lambda v: np.round(10 * v))
        
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

        self.W = np.random.randn(input_size, hidden_size) * DAMPING  # Input -> hidden
        self.V = np.random.randn(hidden_size, hidden_size) * DAMPING # Hidden -> hidden
        self.U = np.random.randn(hidden_size, output_size) * DAMPING # Hidden -> output


        self.b = np.random.randn(hidden_size)
        self.c = np.random.randn(output_size)

        self.hidden_state = None
        self.output_state = None

    def set_properties(self, input_state):
        self.input_state = input_state

        self.hidden_state = self.activation(np.dot(self.input_state, self.W) + self.b)
        self.output_state = self.activation(np.dot(self.hidden_state, self.U) + self.c)

    def backward_passes(self, inputs, *, epochs=5):
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
                y_hat = self.output_activation(np.dot(h, U) + c)

                dY = 2 * (y_hat - y)  # This is equal to \frac{\partial{(y - \hat{y})^2}}{\partial{\theta}} / \frac{\partial{(y - \hat(y))}}{\partial{\theta}} (in LaTeX)

                dW += (dY * U * self.activation_derivative(z).reshape((self.hidden_size, self.output_size)) * x).T
                dU += (dY * z).reshape((self.hidden_size, self.output_size))
                db += (dY * self.activation_derivative(z).reshape((self.hidden_size, self.output_size)) * U).reshape((self.hidden_size))
                dc += dY.reshape((self.output_size))

            self.W -= ALPHA * (dW / length)
            self.U -= ALPHA * (dU / length)
            self.b -= ALPHA * (db / length)
            self.c -= ALPHA * (dc / length)
    
    @property
    def activated_output(self):
        self.output_state = np.dot(self.activation(
            np.dot(self.input_state, self.W) + self.b
        ), self.U) + self.c

        return self.output_activation(self.output_state)

    def reset(self):
        self.input_state = []

        self.W = np.random.randn(self.input_size, self.hidden_size) * DAMPING  # Input -> hidden
        self.V = np.random.randn(self.hidden_size, self.hidden_size) * DAMPING # Hidden -> hidden
        self.U = np.random.randn(self.hidden_size, self.output_size) * DAMPING # Hidden -> output


        self.b = np.random.randn(self.hidden_size)
        self.c = np.random.randn(self.output_size)

        self.hidden_state = None
        self.output_state = None

    def train_on(self, dataset, *, epochs=EPOCHS, min_time=1.5, bar_length=100):
        for _ in utils.Bar(range(epochs), 'training epochs', 'Training complete.', min_time=min_time, length=bar_length):
            self.backward_passes(inputs=dataset)

    def predict(self, inputs):
        self.input_state = inputs
        return self.activated_output[0]
    
    def test(self, dataset=None):
        dataset = dataset or data.DATA
        results = []
        for inp, out in dataset:
            real = self.predict(inp)
            results.append(real == out)
        
        accuracy = sum(results)/len(dataset)
        return accuracy
    
    def train_test(self, train_on, test_on, *, threshold=TESTING_THRESHOLD, epochs=EPOCHS, min_time=1.5, bar_length=100):
        accuracy = 0
        while accuracy < threshold:
            self.train_on(train_on, epochs=epochs, min_time=min_time, bar_length=bar_length)
            accuracy = self.test(test_on)
            print(f"Accuracy: {utils.grade(accuracy * 100)}")
            if accuracy < threshold:
                if accuracy >= 0.5:
                    print("Continuing training")
                else:
                    print("Restarting training.")
                    self.reset()

def interpret_prediction(prediction, sentence):
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    results = []
    while prediction != 1:
        for i, prime in enumerate(primes):
            if prediction % prime == 0:
                results.append(i)
                prediction //= prime
            
            if prediction == 1:
                break
    try:
        if len(results) == 1:
            return sentence[results[0]]
        elif len(results) == 2:
            return sentence[results[0]:results[1]]
    except IndexError:
        return -1 # Error
