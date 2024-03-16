import random
import string

class TextGenerator:
    def __init__(self, starting_word, trigrams) -> None:
        self.starting_word = starting_word
        self.trigrams = trigrams

    def fetch_second_word(self, prev):
        weights = []
        for v in self.trigrams[prev].values():
            weights.append(sum(v.values()))

        return random.choices(list(self.trigrams[prev].keys()), weights=weights)[0]

    def speak_from_word(self, prev2=None, prev=None) -> str:
        if prev2 is None and prev is None:
            return self.starting_word
        
        if prev2 is None:
            return self.fetch_second_word(prev)
        
        if prev not in self.trigrams.get(prev2, []) or prev2 not in self.trigrams:
            return '', 1
        
        return random.choices(list(self.trigrams[prev2][prev].keys()), weights=list(self.trigrams[prev2][prev].values()))[0], 0


    def speak_sentence(self):
        result = []
        prev2 = self.speak_from_word()  # prev2 from context of the 3rd word
        prev = self.speak_from_word(None, prev2)  # prev from context of the 3rd word
        result.append(prev2)
        result.append(prev)
        while True:
            curr, status = self.speak_from_word(prev2, prev)
            result.append(curr)
            if status:
                break
            prev2, prev = prev, curr

        print(formatted(result))

def formatted(text):
    result = ''
    for word in text:
        if word in string.punctuation:
            result = result[:-1]
            result += word + ' '
        elif word[0].isupper() and result:
            result += '. ' + word + ' '
        else:
            result += word + ' '

    return result + '.'
