import enum

# Parts of Speech
class POS(enum.Enum):
    CONJUNCTION = 0
    CARDINAL = 1
    DETERMINER = 2
    EXISTANCE_THERE = 3
    FOREIGN = 4
    PREPOSITION = 5
    ADJECTIVE = 6
    LIST_MARKER = 7
    MODAL = 8
    NOUN = 9
    PREDETERMINER = 10
    POSSESSIVE_ENDING = 11
    PRONOUN = 12
    ADVERB = 13
    PARTICLE = 14
    SYMBOL = 15
    TO = 16
    INTERJECTION = 17
    VERB = 18
    WH_DETERMINER = 19
    WH_PRONOUN = 20
    POSSESSIVE_WH = 21
    WH_ADVERB = 22

    ANY = 23  # The forbidden tag

    def __str__(self):
        return self.name

class WordShape(enum.Enum):
    UPPER = 0
    LOWER = 1
    TITLE = 2       # Like "Hello" where only the first character is capitalized
    MIXED = 3       # Like "HelloWorld" where 1 word has more than 1 but not all letters capitalized
    WITH_DIGITS = 4 # Like "Hello123" where the input has words and digits
    ONLY_DIGITS = 5

class TokenizeType(enum.Enum):
    WORD = 0
    PUNC_SENT = 1
    WORD_SENT = 2

class BigramsDict(dict):
    def fetch_map(self, key):
        possibilities = [{obj.pos: val} for obj, val in self.items() if obj.word == key.word]
        merged = {key: val for dic in possibilities for key, val in dic.items()}        

        return merged

    def __getitem__(self, __key):
        if __key.pos == POS.ANY:
            options = self.fetch_map(__key)
            if not options: return ValueError("Cannot find word")
            return options

        return super().__getitem__(__key)


def word_exists_in(word, target: dict):
    for key in target.keys():
        if word == key:
            return True
    
    return False

class WordShell:
    def __init__(self, word: str, pos: POS) -> None:
        self.word = word
        self.pos = pos

    def __hash__(self) -> int:
        return hash((self.word, self.pos))
    
    def __eq__(self, __value: object) -> bool:
        if not __value: return False

        if isinstance(__value, str):
            return self.word == __value
        
        if __value.pos == POS.ANY or self.pos == POS.ANY:
            return self.word == __value.word

        return (self.word, self.pos) == (__value.word, __value.pos)

    def __repr__(self) -> str:
        return f"{self.word}({self.pos})"
    
class Word:
    def __init__(self, word: str, index: int, punc_index: int) -> None:
        self.word = word
        self.sentence: Sentence = None
        self.index: int = index
        self.punc_index: int = punc_index
        self.pos = None
        
    @property
    def shape(self) -> WordShape:
        # We cannot just do word.islower() or word.isupper() because those functions ignore digits.
        if all([i.islower() for i in self.word]): 
            return WordShape.LOWER
        
        if all([i.isupper() for i in self.word]): 
            return WordShape.UPPER
        
        if self.word.isdigit(): 
            return WordShape.ONLY_DIGITS
        
        if self.word[0].isupper() and all([i.islower() for i in self.word[1:]]): 
            return WordShape.TITLE
        
        if all([i.islower() or i.isupper() for i in self.word]):
            return WordShape.MIXED
        
        return WordShape.WITH_DIGITS

    @property
    def length(self) -> int:
        return len(self.word)
    
    @property
    def capitalization(self) -> bool:
        return self.word[0].isupper()
    
    @property
    def context(self) -> tuple:
        """ Returns a tuple of 2 words """
        if self.sentence is None:
            raise ValueError("Sentence not yet initialized")

        if self.index == 0: return (None, self.sentence.word_only_list[self.index+1])
        if self.index == self.sentence.word_only_length - 1: return (self.sentence.word_only_list[self.index-1], None)
        return self.sentence.word_only_list[self.index-1], self.sentence.word_only_list[self.index+1]

    def __repr__(self) -> str:
        return self.word
    
    def __getitem__(self, idx: slice | int):
        return self.word[idx]
    
    def endswith(self, substring: str):
        return self.word.endswith(substring)
    
    def lower(self):
        return self.word.lower()
    
    def upper(self):
        return self.word.upper()

class Punctuation:
    def __init__(self, symbol: str, index: int) -> None:
        self.symbol = symbol
        self.index: int = index
        self.sentence = None

    def __repr__(self) -> str:
        return self.symbol

class Sentence:
    def __init__(self, wordlist: list[Word | Punctuation]) -> None:
        self.wordlist = wordlist
        self.word_only_list = [
            word for word in self.wordlist if isinstance(word, Word)
        ]
        for text in self.wordlist:
            text.sentence = self

        self.length = len(self.wordlist)
        self.word_only_length = len(self.word_only_list)

    def __iter__(self):
        return iter(self.wordlist)
    
    def __repr__(self) -> str:
        return f"[{', '.join(str(word) for word in self.wordlist)}]"
    
    def __getitem__(self, index: slice | int):
        if isinstance(index, slice):
            return self.wordlist[index.start:index.stop:index.step]
        return self.wordlist[index:]
