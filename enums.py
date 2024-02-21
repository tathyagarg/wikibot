import enum

class POS(enum.Enum):
    NOUN = 0  # Noun
    VERB = 1  # Verb
    ADJ = 2   # Adjective
    ADV = 3   # Adverb
    PRON = 4  # Pronoun
    PREP = 5  # Preposition
    CONJ = 6  # Conjunction
    INTJ = 7  # Interjection
    DET = 8   # Determiner
    PART = 9  # Particle
    PUNC = 10 # Punctuation

class WordShape(enum.Enum):
    UPPER = 0
    LOWER = 1
    TITLE = 2       # Like "Hello" where only the first character is capitalized
    MIXED = 3       # Like "HelloWorld" where 1 word has more than 1 but not all letters capitalized
    WITH_DIGITS = 4 # Like "Hello123" where the input has words and digits
    ONLY_DIGITS = 5
