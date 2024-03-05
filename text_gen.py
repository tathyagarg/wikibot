import random
import constants as consts

class TextGenerator:
    def __init__(self, bigrams: dict[dict[str, int]]) -> None:
        self.bigrams = bigrams

    def speak_from_word(self, start_on: consts.WordShell) -> str:
        # TODO
        ...
        