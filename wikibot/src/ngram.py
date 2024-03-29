import utils

class Trigrams:
    def __init__(self, words: list[utils.Word]) -> None:
        self.words = words
        self.grams: dict[str, dict[str, dict[str, float]]] = {}
        self.make_trigrams()

        self.first: str = words[0].capitalize()

    def make_trigrams(self) -> None:
        """ Populates the grams dictionary with trigrams """
        for prev2, prev, curr in zip(self.words[:-2], self.words[1:-1], self.words[2:]):
            gram_prev2 = self.grams.get(prev2)
            if gram_prev2 is None:
                self.grams[prev2] = {}  # Create a dictionary if one does not exist already
            
            gram_prev = self.grams[prev2].get(prev)
            if gram_prev is None:
                self.grams[prev2][prev] = {}  # Create a dictionary if one does not exist already

            gram_curr = self.grams[prev2][prev].get(curr)
            if gram_curr is None:
                self.grams[prev2][prev][curr] = 0  # Initialize the word with frequency = 0, as the frequency is instantly increased in the next line
            
            self.grams[prev2][prev][curr] += 1

        for k, v in self.grams.items():
            for k2, v2 in v.items():
                v2_sum = sum(v2.values())
                for k3, v3 in v2.items():
                    self.grams[k][k2][k3] = v3/v2_sum  # Smooth the probabilities
