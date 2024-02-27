import enum
import random
import math
import hashlib

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
    POS = 9   # Possessive
    PUNC = 10 # Punctuation
    QUAN = 11 # Quantifier
    INTR = 12 # Interrogative adverb
    HELP = 13 # Helping verbs

def activation(num: float) -> float:
    return 1/((1/100) + math.exp(-num-math.log(100)))

class Node:
    def __init__(self) -> None:
        self.incoming: list[Node] = []
        self.outgoing: list[Node] = []
        self.biases: list[float] = []

        self._value = 0

    def set_biases(self) -> None:
        if not self.incoming:
            return ValueError("Incoming nodes not set")
        self.biases = [1]*(len(self.incoming)+1)
        # 1 is an arbitrary starting value. The starting value can be anything, but it gets worse as it approaches 0

    @property
    def value(self) -> float:
        if self.incoming and self.biases:
            income = 0
            for bias, value in zip(self.biases, [InputNode(), *self.incoming]):
                #print(bias, value.value)
                income += bias*value.value
            return activation(income)
        return self._value

    @value.setter
    def value(self, new: float):
        if self.incoming:
            raise ValueError("Attempting to set value for node that is not in input layer")
        self._value = new

    @classmethod
    def connect(cls, left, right):
        for node in left:
            node.outgoing = right
        for node in right:
            node.incoming = left

    def __repr__(self) -> str:
        return str(self.value)

class InputNode(Node):
    def __init__(self) -> None:
        super().__init__()

class OutputNode(Node):
    def __init__(self) -> None:
        super().__init__()

    @property
    def value(self):
        if self.incoming and self.biases:
            income = sum([bias*value.value for bias, value in zip(self.biases, [InputNode(), *self.incoming])])
            print([node.value for node in self.incoming])
            return activation(round(income)/1000)
        return self._value

class HiddenNode(Node):
    def __init__(self) -> None:
        super().__init__()

def truncated_hash(string):
    sha256_hash = hashlib.sha256(string.encode()).hexdigest()
    hash_integer = int(sha256_hash[:10], 16)
    return (hash_integer % (10 ** 10)) / (10**9)

def convert(num: float) -> int:
    return round(1/(
        (1/14) + math.exp(-num-math.log(14))
    ))

def dec_to_tri(num: int) -> list[int]:
    items = []
    while num != 0:
        items.append(num%3)
        num = math.floor(num/3)
    if len(items) < 3: items.extend([0]*(3-len(items)))
    return items[::-1]


def train(training_data: list[tuple[str, str, str, POS]], x):
    inputs = [InputNode(), InputNode(), InputNode()]
    for i, node in enumerate(inputs):
        node.value = truncated_hash(training_data[0][i])

    output = [OutputNode()]

    hidden = [HiddenNode() for _ in range(5)]

    Node.connect(inputs, hidden)
    Node.connect(hidden, output)

    for node in hidden:
        node.set_biases()
    for node in output:
        node.set_biases()

    result = 100
    iter_limit = 10_000

    for node in hidden:
        record = []
        mul_map = {
            0: 1,
            1: x,
            2: 1/1-x
        }
        original = node.biases
        for i in range(27):
            for index, val in enumerate(dec_to_tri(i)):
                node.biases[index] = mul_map[val]
            record.append(output[0].value)
            node.biases = original
        min_idx = record.index(min(record))
        for index, val in enumerate(dec_to_tri(min_idx)):
            node.biases[index] *= mul_map[val]
        
        print(record, min(record), convert(min(record)))

"""        ...
    return [[
        node.biases for node in curr
    ] for curr in [hidden, output]], iter_limit"""

print(train([
    ("how", "are", "you", POS.VERB),
    ("I", "am", "good", POS.VERB),
    ("", "how", "are", POS.INTR)
], 5))
