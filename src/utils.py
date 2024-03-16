import enum
import random
import toml
import time
import colorama

class Project:
    def __init__(self) -> None:
        self.POS_TAGGER = {
            "PERCEPTRON_PICKLE": None
        }

        self.QUERY_ANALYZER = {
            "DAMPING": None,
            "ALPHA": None,
            "EPOCHS": None,
            "TESTING_THRESHOLD": None
        }

        self.UTILS = {
            "HASH_CHARACTER": None,
            "SPACE_CHARACTER": None
        }

        self.data = [self.POS_TAGGER, self.QUERY_ANALYZER, self.UTILS]

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
    PROJECT.QUERY_ANALYZER['TESTING_THRESHOLD'] = data['query-analyzer']['TESTING_THRESHOLD']
    
    PROJECT.UTILS['HASH_CHARACTER'] = data['utils']['HASH_CHARACTER']
    PROJECT.UTILS['SPACE_CHARACTER'] = data['utils']['SPACE_CHARACTER']

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
    
    def __repr__(self):
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

    def lower(self):
        return self.word.lower()

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

def make_words(words):
    if isinstance(words[0], list):
        return [Word(i, -1, -1) for sent in words for i in sent]
    return [Word(i, -1, -1) for i in words]

def convert_tagged(tagged_words):
    if isinstance(tagged_words[0], list):
        return [[WordShell(i.word, STR_TO_POS[pos]) for i, pos in words] for words in tagged_words]
    return [WordShell(i.word, STR_TO_POS[pos]) for i, pos in tagged_words]

def make_sentences(words: list[list[str]], tagger) -> Sentence:
    words = make_words(words)
    tagged = tagger.tag(words)

    converted = convert_tagged(tagged)
    sentences = [Sentence(sent) for sent in converted]
    
    return sentences

class Bar:
    def __init__(self, rng, final_msg, exit_msg, *, min_time=0.001, length=100, hash_character=PROJECT.UTILS["HASH_CHARACTER"], space_character=PROJECT.UTILS["SPACE_CHARACTER"]) -> None:
        if isinstance(rng, list): rng = range(len(rng)+1)
        self.rng = rng

        self.start_time = -1
        self.time = -1
        self.min_time = min_time
        self.length = length

        self.maximum = self.rng.stop
        self.thresh = self.maximum / self.length

        self.hash_character = hash_character
        self.space_character = space_character

        self.final_message = final_msg
        self.exit_message = exit_msg

    def render(self, item):
        if item == -1:
            hash_count = self.length
            space_count = 0
            item = self.maximum
        else:
            hash_count = int(item // self.thresh)
            space_count = self.length - hash_count

        return '[' + self.hash_character*hash_count + self.space_character*space_count + f'] {item/self.maximum * 100:.2f}% ({item}/{self.maximum}) {self.final_message}'
    
    def iterations(self):
        for item in self.rng:
            curr = time.time()
            if self.time == -1:
                self.start_time = curr
                self.time = curr
            elif (curr - self.time) < self.min_time:
                yield item
                continue
            else:
                self.time = curr
            print(self.render(item), end='\r')
            yield item

    def __iter__(self):
        iterator = self.iterations()
        while True:
            try:
                yield next(iterator)
            except StopIteration:
                print(self.render(-1))
                print(self.exit_message)
                return

def pad(tag_only, padding_character=-1, length=10):
    null_count = [padding_character] * (length-len(tag_only))
    return tag_only + null_count

def grade(number):
    number = round(number, 2)
    color = colorama.Fore.RED if 0 <= number < 50 else (colorama.Fore.YELLOW if 50 <= number < 90 else colorama.Fore.GREEN)

    return f'{color}{number}%{colorama.Style.RESET_ALL}'

def flatten(items):
    result = []
    for sub in items:
        result.extend(sub)
    return result
