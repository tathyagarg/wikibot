import constants as consts

class Word:
    def __init__(self, word: str, index: int, punc_index: int) -> None:
        self.word = word
        self.sentence: Sentence = None
        self.index: int = index
        self.punc_index: int = punc_index
        self.pos = None
        
    @property
    def shape(self) -> consts.WordShape:
        # We cannot just do word.islower() or word.isupper() because those functions ignore digits.
        if all([i.islower() for i in self.word]): 
            return consts.WordShape.LOWER
        
        if all([i.isupper() for i in self.word]): 
            return consts.WordShape.UPPER
        
        if self.word.isdigit(): 
            return consts.WordShape.ONLY_DIGITS
        
        if self.word[0].isupper() and all([i.islower() for i in self.word[1:]]): 
            return consts.WordShape.TITLE
        
        if all([i.islower() or i.isupper() for i in self.word]):
            return consts.WordShape.MIXED
        
        return consts.WordShape.WITH_DIGITS

    @property
    def length(self) -> int:
        return len(self.word)
    
    @property
    def prefix(self) -> str:
        return ""
    
    @property
    def suffix(self) -> str:
        return ""
    
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
