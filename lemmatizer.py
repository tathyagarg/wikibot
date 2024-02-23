import constants as consts
from collections import namedtuple

feature_fields = ["word", "shape", "length", "suffix", "prefix", "context", "frequency", "capitalization"]


def generate_features(
    word: str, 
    shape: consts.WordShape, 
    length: int, 
    suffix: None | str, 
    prefix: None | str, 
    context: list[str | None], 
    frequency: int, 
    capitalization: bool  # Word is all capital, discounting numbers
) -> dict:
    return dict(zip(feature_fields, [word, shape, length, suffix, prefix, context, frequency, capitalization]))


def get_word_shape(word: str) -> consts.WordShape:    
    # We cannot just do word.islower() or word.isupper() because those functions ignore digits.
    if all([i.islower() for i in word]): 
        return consts.WordShape.LOWER
    
    if all([i.isupper() for i in word]): 
        return consts.WordShape.UPPER
    
    if word.isdigit(): 
        return consts.WordShape.ONLY_DIGITS
    
    if word[0].isupper() and all([i.islower() for i in word[1:]]): 
        return consts.WordShape.TITLE
    
    if all([i.islower() or i.isupper() for i in word]): 
        return consts.WordShape.MIXED
    
    return consts.WordShape.WITH_DIGITS


def find_suffix(word: str) -> str:
    # TODO: Give this actual functionality
    return False


def find_prefix(word: str) -> str:
    # TODO: Give this actual functionality
    return False


def fetch_context(sentence: list[str], index: int) -> list[str]:
    if index == 0: return [None, sentence[1]]
    elif index == len(sentence) - 1: return [sentence[index-1], None]
    return [sentence[index-1], sentence[index+1]]


def classify(sentence: list[str], append_item: list, frequencies: dict[str, int]):
    for i, word in enumerate(sentence):
        append_item.append(generate_features(
            word,
            get_word_shape(word),
            len(word),
            find_suffix(word),
            find_prefix(word),
            fetch_context(sentence, i),
            frequencies.get(word, 1),
            word.isupper()
        ))
        frequencies[word] = frequencies.get(word, 0) + 1
    return append_item, frequencies



class Lemmatizer:
    def __init__(self, text: list[list[str]]) -> None:
        self.text = text

    def classify(self, idx: int, sentence: list[dict], word: dict) -> tuple[tuple[str, consts.POS], int]:
        """
        Function that classifies the given word into a part of speech.
        Return:
            tuple[tuple[str (a), consts.POS (b)], int (c)]
        (a) - The word itself
        (b) - The word's part of speech
        (c) - The number of words to skip. Used in check 3.

        @idx: int - The current index
        @sentence: list[dict] - The sentence being parsed
        @word: dict - The features of the word being parsed

        After some (very little) thinking, sentences observe to follow a pattern.
        The pattern can be written in a notation where:
            (a/b) represents 'a or b'
            {a}   represents '>=0 instances of a'
            [a]   represents '<=1 instance of a'
            and the numbers correspond to the indexes in constants.POS
        (4/[7]{2{8}}0)1{3}(1/2/4/[7]{2{8}}0)[(1/2/4/[7]{2{8}}0)]{6(4/[7]{2{8}}0)1{3}(1/2/4/[7]{2{8}}0)[(1/2/4/[7]{2{8}}0)]}
        """

        """ Check 1 - determiners """
        if word['word'].lower() in consts.DETERMINERS:
            return (word['word'], consts.POS.DET), 0
        
        """ Check 2 - pronouns """
        if word['word'].lower() in consts.PRONOUNS:
            return (word['word'], consts.POS.PRON), 0

        """
            Check 3 - nouns and adjectvives

            PART A: Adjectives
                Check I: Preceding word is a determiner
                        Example: The tasty, Italian food is ...
                    1. When the program reaches 'tasty', it sees the previous word was a determiner.
                    2. It skips ahead over the list until it finds the first noun.
                    3. It then jumps back to tasty and counts the numbers of words from the determiner to the noun.
                    4. If the number is 0, the current word is a noun! Free noun identification as a side effect.
                    5. If the number is = 1, the current word is an adjective.
                    6. If the number is >= 2, a few of the following words are adjectives too, which may include particles like 'of' in 'few of'.
                Check II: Preceding word is a verb
                        Example: He only eats tasty food.
                    1. The program reaches 'tasty', and sees the preceding word is a verb.
                    2. The program then does the same steps as in Check I to find the adjectives.

            PART B: Nouns
                TODO
        """
        # TODO


    def tag_part_of_speech(self, sentence_idx: int = -1) -> list[list[tuple[str, consts.POS]]]:
        """
            The output of this function would be in the form:
            [ [ ( str, POS ) ] ]
        """
        result = []
        target = self.extract_features(sentence_idx)
        if sentence_idx == -1:
            for sentence in target:
                result.append([])
                for idx, word in enumerate(sentence):
                    result[-1].append(self.classify(idx, word))
        else:
            for idx, word in enumerate(target):
                result.append(self.classify(idx, word))

        return result
    
    def extract_features(self, sentence_idx: int = -1) -> list[list[dict] | dict]:
        """
            Depending on the @sentence_idx parameter, the function will either return a "list of list of dicts" or a "list of dicts"
            If @sentence_idx is -1, you get a list[list[dict]]
            Otherwise, you get a list[dict]. This list contains the feature dict of every word in the 'sentence_idx'-th sentence

            Throws an error if the sentence_idx is out of bounds
        """
        result: list = []
        frequencies: dict[str, int] = {}
        if sentence_idx == -1:
            # Disgusting O(n * m) time complexity, but I'm not going to think about it too hard.
            for sentence in self.text:
                result.append([])
                result[-1], frequencies = classify(sentence, result[-1], frequencies)
        else:
            result, _ = classify(self.text[sentence_idx], result, {})
        return result
