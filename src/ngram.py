import utils

class BigramMaker:
    def __init__(self, words: list[str]) -> None:
        self.words = words

        self.bigrams = utils.BigramsDict()

    def fetch_bigrams(self):
        for sentence in self.words:
            # Using len-1 so that we don't run into an error when accessing element i+1
            for i in range(len(sentence)-1):
                curr = sentence[i].lower()
                next_word = sentence[i+1]
                if not self.bigrams.get(curr):
                    # Initializing subdict
                    self.bigrams[curr] = utils.BigramsDict()

                if not self.bigrams.get(curr).get(next_word):
                    self.bigrams[curr][next_word] = 0

                self.bigrams[curr][next_word] += 1
        
        return smooth(self.bigrams)
    
def smooth(bigrams: dict[str, dict[str, int]]) -> dict[str, dict[str, float]]:
    for curr, next_words in bigrams.items():
        total = sum(next_words.values())
        smoothed_probs = utils.BigramsDict.from_dict({
            word: count / total for word, count in next_words.items()
        })
        bigrams[curr] = smoothed_probs

    return bigrams
