import random
import string

class TextGenerator:
    def __init__(self, starting_word: str, trigrams: dict[str, dict[str, dict[str, float]]]) -> None:
        self.starting_word = starting_word
        self.trigrams = trigrams  # Lots of nesting!

    def fetch_second_word(self, prev: str) -> str:
        """
            Returns the second word in a sentence

            :param prev: The previous word (First word)
            :returns: The second word
        """
        return random.choice(list(self.trigrams[prev].keys()))

    def speak_from_word(self, prev2: str = None, prev: str = None) -> str | tuple[str, int]:
        """
            Speaks from given words
            
            :param prev2: The previous to previous word
            :param prev: The previous word
            :returns: The current word (or next word? Not sure which is more appropriate.) along with a status denoting whether we should continue or not (only if we're not at the first two words).
        """
        if prev2 is None and prev is None:  # First word!
            return self.starting_word
        
        if prev2 is None:  # Second word!
            return self.fetch_second_word(prev)
        
        if prev not in self.trigrams.get(prev2, []) or prev2 not in self.trigrams:  # Last word!
            return '', 1
        
        return random.choices(list(self.trigrams[prev2][prev].keys()), weights=list(self.trigrams[prev2][prev].values()))[0], 0


    def speak_sentence(self) -> None:
        """
            Prints out a sentence of spoken words
        """
        result: list[str] = []
        prev2 = self.speak_from_word()  # prev2 from context of the 3rd word
        prev = self.speak_from_word(None, prev2)  # prev from context of the 3rd word
        # (we ignore the status return because it doesn't return a status at this point) ^^^
        result.append(prev2)
        result.append(prev)
        while True:
            curr, status = self.speak_from_word(prev2, prev)
            result.append(curr)
            if status:  # if status == 1:
                break
            prev2, prev = prev, curr

        print(formatted(result))

def formatted(text: list[str]) -> str:
    """
        Returns the words into a formatted paragraph.
        
        :param text: The words (and punctuation) to format
        :returns: A paragraph with spaces between words, no space before punctuation, spacing after punctuation, and first letter of first word of every sentence capitalized.
    """
    result: str = ''
    for word in text:
        if word in string.punctuation:  # Punctuation
            result = result[:-1]
            result += word + ' '
        elif word[0].isupper() and result:  # First word of a sentence
            result += '. ' + word + ' '
        else:
            result += word + ' '  # Regular word

    return result + '.'  # Adds a full stop to the end
