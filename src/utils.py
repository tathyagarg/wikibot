import enum
import random
import toml

class Project:
    def __init__(self) -> None:
        self.POS_TAGGER = {
            "PERCEPTRON_PICKLE": None
        }

        self.QUERY_ANALYZER = {
            "DAMPING": None,
            "ALPHA": None,
            "LAMBDA": None,
            "EPOCHS": None
        }

        self.data = [self.POS_TAGGER, self.QUERY_ANALYZER]

    @property
    def initialized(self):
        for data in self.data:
            if not all(list(data.values())): return False
        return True

with open(f'./config.toml') as f:
    data = toml.load(f)

    PROJECT = Project()
    PROJECT.POS_TAGGER['PERCEPTRON_PICKLE'] = data['pos-tagger']['PERCEPTRON_PICKLE']
    PROJECT.QUERY_ANALYZER['DAMPING'] = data['query-analyzer']['DAMPING']
    PROJECT.QUERY_ANALYZER['ALPHA'] = data['query-analyzer']['ALPHA']
    PROJECT.QUERY_ANALYZER['EPOCHS'] = data['query-analyzer']['EPOCHS']

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

    # The forbidden tag(s)
    ANY = 23
    PUNCTUATION = 24

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

STR_TO_POS = {
    'CC': POS.CONJUNCTION,
    'CD': POS.CARDINAL,
    'DT': POS.DETERMINER,
    'EX': POS.EXISTANCE_THERE,
    'FW': POS.FOREIGN,
    'IN': POS.PREPOSITION,
    'JJ': POS.ADJECTIVE, 'JJR': POS.ADJECTIVE, 'JJS': POS.ADJECTIVE,
    'LS': POS.LIST_MARKER,
    'MD': POS.MODAL,
    'NN': POS.NOUN, 'NNS': POS.NOUN, 'NNP': POS.NOUN, 'NNPS': POS.NOUN,
    'PDT': POS.PREDETERMINER,
    'POS': POS.POSSESSIVE_ENDING,
    'PRP': POS.PRONOUN, 'PRP$': POS.PRONOUN,
    'RB': POS.ADVERB, 'RBR': POS.ADVERB, 'RBS': POS.ADVERB,
    'RP': POS.PARTICLE,
    'SYM': POS.SYMBOL,
    'TO': POS.TO,
    'UH': POS.INTERJECTION,
    'VB': POS.VERB, 'VBD': POS.VERB, 'VBG': POS.VERB, 'VBN': POS.VERB, 'VBP': POS.VERB, 'VBZ': POS.VERB,
    'WDT': POS.WH_DETERMINER,
    'WP': POS.WH_PRONOUN,
    'WP$': POS.POSSESSIVE_WH,
    'WRB': POS.WH_ADVERB,
    'PUNC': POS.PUNCTUATION
}

class BigramsDict:
    # Based off of a dict

    @classmethod
    def from_dict(cls, initializing_values: dict):
        bigrams = cls()
        bigrams.put_items(initializing_values, override=True)
        return bigrams

    def __init__(self) -> None:
        self.__items = {}
    
    def items(self):
        return self.__items.items()
    
    @property
    def _items(self) -> list[tuple]:
        return list(self.items())

    def values(self):
        return self.__items.values()
    
    @property
    def _values(self) -> list:
        return list(self.values())

    def keys(self):
        return self.__items.keys()

    @property
    def _keys(self):
        return list(self.keys())

    def fetch_map(self, key):
        possibilities = [{obj.pos: val} for obj, val in self.items() if obj.word == key.word]
        merged = {key: val for dic in possibilities for key, val in dic.items()}

        return merged
    
    def __setitem__(self, __key, __value):
        self.__items[__key] = __value

    def __getitem__(self, __key):
        if __key.pos == POS.ANY:
            options = self.fetch_map(__key)
            
            # Guard clause
            if not options:
                raise KeyError("Cannot find word")

            return options
        
        for current_key, val in self.items():
            if current_key == __key:
                return val
            
        raise KeyError("Cannot find word")
    
    def __contains__(self, __key: object) -> bool:
        try:
            self.__getitem__(__key)
            return True
        except KeyError:
            return False

    def get(self, __key: object, __default = None) -> object | None:
        try:
            value = self.__getitem__(__key)
            return value
        except KeyError:
            return __default

    def random_choice(self, **kwargs) -> tuple | object:
        weight_values = kwargs.get('weight_values')
        if weight_values:
            # Use the values as weights
            choices, weights = self._keys, self._values
            return random.choices(choices, weights=weights, k=1)[0]

        return random.choice(list(self.items()))

    def __repr__(self) -> str:
        # WOW!
        return "BigramsDict{{{0}}}".format(', '.join(['{0}: {1}'.format(key, value) for key, value in self.items()]))

    def put_items(self, vals: dict, **kwargs):
        override = kwargs.get('override')
        if override:
            self.__items = vals
        else:
            self.__items.update(vals)

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
    
    def __str__(self) -> str:
        return self.word
    
    def lower(self):
        return WordShell(self.word.lower(), self.pos)
    
    def upper(self):
        return WordShell(self.word.upper(), self.pos)
    
    def title(self):
        return WordShell(self.word.title(), self.pos)
    
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
        return f"[{', '.join([str(word) for word in self.wordlist])}]"
    
    def __getitem__(self, index: slice | int):
        if isinstance(index, slice):
            return self.wordlist[index.start:index.stop:index.step]
        return self.wordlist[index]
    
    def __len__(self) -> int:
        return len(self.wordlist)
    
    def fix_syntax(self):
        """
        Rules:
            First word is capitalized
        """
        items = []
        for i, word in enumerate(self.wordlist):
            if i == 0: items.append(word.title())
            else: items.append(word)

        sent = Sentence(items)
        return sent

    def joint(self) -> str:
        result = ''
        for word in self.wordlist:
            if word.pos != POS.PUNCTUATION:
                result += f' {word.word}'
            else:
                result += word.word
        
        return result.strip()

class CompleteSentence(Exception):
    ...

def make_sentences(words: list[list[str]], tagger) -> Sentence:
    words = [[Word(i, -1, -1) for i in sent] for sent in words]
    tagged = tagger.tag(words)

    converted = [[WordShell(i.word, STR_TO_POS[pos]) for i, pos in sent] for sent in tagged]
    sentences = [Sentence(sent) for sent in converted]
    
    return sentences
