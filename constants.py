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

class WordShape(enum.Enum):
    UPPER = 0
    LOWER = 1
    TITLE = 2       # Like "Hello" where only the first character is capitalized
    MIXED = 3       # Like "HelloWorld" where 1 word has more than 1 but not all letters capitalized
    WITH_DIGITS = 4 # Like "Hello123" where the input has words and digits
    ONLY_DIGITS = 5
