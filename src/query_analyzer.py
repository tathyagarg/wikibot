import numpy as np
import utils
import math
import data
import warnings
import typing

warnings.filterwarnings("error")  # Treat warnings as errors

analyzer_env = utils.PROJECT.QUERY_ANALYZER

DAMPING = analyzer_env['DAMPING']
ALPHA = analyzer_env['ALPHA']
EPOCHS = analyzer_env['EPOCHS']
TESTING_THRESHOLD = analyzer_env['TESTING_THRESHOLD']

DATASET = list[tuple[list[int], int]]

class RecurrentNeuralNetwork:
    def __init__(
        self, input_size: int, hidden_size: int, output_size: int, *, 
        activation: typing.Callable = None, 
        activation_deriv: typing.Callable = None, 
        output_activation: typing.Callable = None
    ) -> None:
        self.input_state: list[int] = []

        if activation_deriv and not activation or activation and not activation_deriv:
            raise KeyError("Must include both activation and activation_deriv")

        self.activation = activation or np.tanh
        self.activation_derivative = activation_deriv or (lambda v: 1/np.cosh(v)**2) # d(tanhx)/dx = sech^2(x)
        self.output_activation = output_activation or (lambda v: np.round(10 * v))
        
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

        self.W = np.random.randn(input_size, hidden_size) * DAMPING  # Input -> hidden
        self.U = np.random.randn(hidden_size, output_size) * DAMPING # Hidden -> output


        self.b = np.random.randn(hidden_size)
        self.c = np.random.randn(output_size)

        self.hidden_state: list[float] = None
        self.output_state: list[float] = None

    def backward_passes(self, inputs: DATASET, *, epochs: int = 5) -> None:
        """ 
            Backward passes and recomputes the weights and biases
            Fromulas used (under default conditions):
                dY = 2 * (y_hat - y)
                dW = dY * U * x * sech^2(z)
                dU = dY * z
                db = dY * U * sech^2(z)
                dc = dY

            :param inputs: The input data on which the model is being trained
            :param epochs: The number of times the model trains the set of inputs (default is 5)
        """
        for _ in range(epochs):
            # Initialize as zeros
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

                try:
                    dW += (dY * U * self.activation_derivative(z).reshape((self.hidden_size, self.output_size)) * x).T
                    dU += (dY * z).reshape((self.hidden_size, self.output_size))
                    db += (dY * self.activation_derivative(z).reshape((self.hidden_size, self.output_size)) * U).reshape((self.hidden_size))
                    dc += dY.reshape((self.output_size))
                except RuntimeWarning:
                    raise RuntimeError  # RuntimeError when overflow

            # Update our weights and biases
            self.W -= ALPHA * (dW / length)
            self.U -= ALPHA * (dU / length)
            self.b -= ALPHA * (db / length)
            self.c -= ALPHA * (dc / length)
    
    @property
    def activated_output(self) -> float:
        """ 
            Calculates the output_state, and returns output_activation(output_state)
            Formula used:
                output_state = U * ((W * input) + b) + c
        """
        self.output_state = np.dot(self.activation(
            np.dot(self.input_state, self.W) + self.b
        ), self.U) + self.c

        return self.output_activation(self.output_state)

    def reset(self) -> None:
        """ Reset weights, biases, and states """
        self.input_state = []

        self.W = np.random.randn(self.input_size, self.hidden_size) * DAMPING  # Input -> hidden
        self.U = np.random.randn(self.hidden_size, self.output_size) * DAMPING # Hidden -> output
        self.b = np.random.randn(self.hidden_size)
        self.c = np.random.randn(self.output_size)

        self.hidden_state = None
        self.output_state = None

    def train_on(
        self, dataset: DATASET, *, 
        epochs: int = EPOCHS,
        min_time: float = 1.5,
        bar_length: int = 100
    ) -> None:
        """
            Trains the Recurrent NN model
            
            :param dataset: The dataset on which to train the model on
            :param epochs: Number of epochs to train on
            :param min_time: Number of seconds to wait before updating progress bar (defaults to 1.5s)
            :param bar_length: Length of the progress bar (defaults to 100 characters)
        """
        for _ in utils.Bar(rng=range(epochs), final_msg='training epochs', exit_msg='Training complete.', min_time=min_time, length=bar_length):
            # Train while displaying progress bar
            self.backward_passes(inputs=dataset)

    def predict(self, inputs: list[int]) -> int:
        """ Predicts an output for the given input """
        self.input_state = inputs
        return self.activated_output[0]
    
    def test(self, dataset: DATASET = None) -> float:
        """
            Tests the model on the given dataset

            :param dataset: The dataset on which to test the model (defaults to data.DATA)
            :returns: The accuracy of the model
        """
        dataset = dataset or data.DATA
        results: list[bool] = []
        for inp, out in dataset:
            real: int = self.predict(inp)
            results.append(real == out)
        
        accuracy: float = sum(results)/len(dataset)
        return accuracy
    
    def train_test(
        self, train_on: DATASET, test_on: DATASET, *, 
        threshold: float = TESTING_THRESHOLD, 
        epochs: int = EPOCHS, 
        min_time: float = 1.5, 
        bar_length: int = 100
    ) -> None:
        """
            Trains and tests the model
            
            :param train_on: The dataset to train the model on
            :param test_on: The dataset to test the model on
            :param threshold: The minimum accuracy threshold to pass
            :param min_time: Number of seconds to wait before updating progress bar (defaults to 1.5s)
            :param bar_length: Length of the progress bar (defaults to 100 characters)
        """
        accuracy: float = 0
        while accuracy < threshold:
            try:
                self.train_on(train_on, epochs=epochs, min_time=min_time, bar_length=bar_length)
                accuracy = self.test(test_on)
                print(f"Accuracy: {utils.grade(accuracy * 100)}")
                if accuracy < threshold:
                    if accuracy >= 0.5:
                        print("Continuing training")  # Satisfactory accuracy
                    else:
                        print("Restarting training.")  # Unsatisfactory accuracy
                        self.reset()
            except RuntimeError:
                # Instantly restart after overflow
                print("Encountered overflow. Restarting training.")
                self.reset()

def interpret_prediction(prediction: int, sentence: list[int]) -> utils.WordShell | list[utils.WordShell]:
    """
        Decode prime index to get decimal index
        For example, 
            2 => index 0
            3 => index 1
            6 => slice 0:1 (characters 0, 1)
            55 => slice 2:4 (characters 2, 3, 4)

        :param prediction: The prediction from RecurrentNeuralNetwork.predict
        :param sentence: The input sentence to RecurrentNeuralNetwork.predict
        :returns: The word (or words) corresponding to the given prediction on the given sentence
    """
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    results: list[int] = []  # The primes that factor our prediction
    while prediction != 1:
        for i, prime in enumerate(primes):
            if prediction % prime == 0:
                results.append(i)
                prediction //= prime
            
            if prediction == 1:  # Break when the prediction becomes 1
                break
    try:
        if len(results) == 1:
            return sentence[results[0]]  # Return a single word
        elif len(results) == 2:
            return sentence[results[0]:results[1]]  # Return a slice
    except IndexError:
        return -1 # Error
