import random

class TextGenerator:
    def __init__(self, bigrams: dict[dict[str, int]]) -> None:
        self.bigrams = bigrams

    def speak_word(self, start_on: str) -> str:
        return random.choices(list(self.bigrams[start_on].keys()), weights=list(self.bigrams[start_on].values()), k=1)[0]        

