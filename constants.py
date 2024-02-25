import enum

# Parts of Speech
class POS(enum.Enum):
    NOUN = 0  # Noun
    VERB = 1  # Verb
    ADJ = 2   # Adjective
    ADV = 3   # Adverb
    PRON = 4  # Pronoun
    PREP = 5  # Preposition
    CONJ = 6  # Conjunction
    PART = 7  # Particle
    ART = 8   # Article
    POS = 9  # Possessive

class WordShape(enum.Enum):
    UPPER = 0
    LOWER = 1
    TITLE = 2       # Like "Hello" where only the first character is capitalized
    MIXED = 3       # Like "HelloWorld" where 1 word has more than 1 but not all letters capitalized
    WITH_DIGITS = 4 # Like "Hello123" where the input has words and digits
    ONLY_DIGITS = 5

ARTICLES = ["a", "an", "the"]
POSSESSIVES = ["my", "your", "his", "her", "its", "our", "their"]
DEMONSTRATIVES = ["this", "that", "these", "those"]
PRONOUNS = ["i", "me", "you", "he", "him", "she", "her", "it", "we", "us", "they", "them"]
CONJUCTIONS = ["and", "but"]
VERBS = ["am", "are", "is"]
NOUNS = ["food", "brother", "boy"]
ADVERBS = ["not", "always"]

DIRECT = [
    (ARTICLES, POS.ART),
    (PRONOUNS, POS.PRON),
    (CONJUCTIONS, POS.CONJ),
    (POSSESSIVES, POS.POS)
]
