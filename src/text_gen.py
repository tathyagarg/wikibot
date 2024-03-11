import random
import utils

class TextGenerator:
    def __init__(self, bigrams: utils.BigramsDict) -> None:
        self.bigrams = bigrams

    def speak_from_word(self, start_on: utils.WordShell) -> str:
        possibilities = self.bigrams.get(start_on)  # Safer than __getitem__

        if not possibilities:
            raise utils.CompleteSentence("Cannot think of further words.")

        if start_on.pos == utils.POS.ANY:
            # possibilities: dict[ utils.POS, BigramsDict[ WordShell, float ] ]

            key: utils.POS = random.choice(list(possibilities.keys()))

            # We can use __getitem__ instead of BigramsDict.get() because 'key' is guaranteed to be in the dict
            return key, possibilities[key].random_choice(weight_values=True)

        return None, possibilities.random_choice(weight_values=True)
