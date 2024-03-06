import random
import constants as consts

class TextGenerator:
    def __init__(self, bigrams: consts.BigramsDict) -> None:
        self.bigrams = bigrams

    def speak_from_word(self, start_on: consts.WordShell) -> str:
        possibilities = self.bigrams.get(start_on)  # Safer than __getitem__

        if not possibilities:
            raise consts.CompleteSentence("Cannot think of further words.")

        if start_on.pos == consts.POS.ANY:
            # possibilities: dict[ consts.POS, BigramsDict[ WordShell, float ] ]

            key: consts.POS = random.choice(list(possibilities.keys()))

            # We can use __getitem__ instead of BigramsDict.get() because 'key' is guaranteed to be in the dict
            return key, possibilities[key].random_choice(weight_values=True)

        return None, possibilities.random_choice(weight_values=True)
