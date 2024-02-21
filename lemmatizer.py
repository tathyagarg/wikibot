import enums as e
from collections import namedtuple

feature_fields = ["word", "shape", "length", "suffix", "prefix", "context", "frequency", "capitalization"]

def generate_features(
    word: str, 
    shape: e.WordShape, 
    length: int, 
    suffix: None | str, 
    prefix: None | str, 
    context: list[str | None], 
    frequency: int, 
    capitalization: bool  # Word is all capital, discounting numbers
) -> dict:
    return dict(zip(feature_fields, [word, shape, length, suffix, prefix, context, frequency, capitalization]))

def get_word_shape(word: str) -> e.WordShape:    
    # We cannot just do word.islower() or word.isupper() because those functions ignore digits.
    if all([i.islower() for i in word]): return e.WordShape.LOWER
    elif all([i.isupper() for i in word]): return e.WordShape.UPPER
    elif word.isdigit(): return e.WordShape.ONLY_DIGITS
    elif word[0].isupper() and all([i.islower() for i in word[1:]]): return e.WordShape.TITLE
    elif all([i.islower() or i.isupper() for i in word]): return e.WordShape.MIXED
    else: return e.WordShape.WITH_DIGITS

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

    def tag_part_of_speech(self) -> list[list[tuple[str, e.POS]]]:
        """
            The output of this function would be in the form:
            [ [ ( str, POS ) ] ]
        """
        ...
    
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
