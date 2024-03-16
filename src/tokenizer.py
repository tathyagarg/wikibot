import re
import utils

def purify(text: list[str]) -> list[str]:
    return [i.strip() for i in text if i is not None and i.strip()]

class Tokenizer:
    CONTRACTIONS = {
        "can't": ["can", "not"],
        "won't": ["will", "not"],
        "wouldn't": ["would", "not"],
        "shouldn't": ["should", "not"]
    }
    def __init__(self, text: str) -> None:
        self.text: str = text
        
    def tokenize_word(self, punctaution: bool = False, target=None) -> list[str]:
        target = target or self.text
        pattern: str = r"[^\w']+" if not punctaution else r"\b[\w'-]+\b|\S"
        
        result: list[str] = re.findall(pattern, target)
        return purify(result)

    def tokenize_word_sent(self, punctuation: bool = False) -> list[list[str]]:
        result = [self.tokenize_word(punctuation, i) for i in self.text]
        return result

    def tokenize_punc_sent(self) -> list[list[str]]:
        result = purify(re.split(r'(\W)', self.text))
        return result
    
    def break_contractions_on(self, acting_on: utils.TokenizeType) -> list[str]:
        if acting_on == utils.TokenizeType.WORD:
            return self.break_contractions(self.tokenize_word(True))
        
        if acting_on == utils.TokenizeType.PUNC_SENT:
            return self.break_contractions(self.tokenize_punc_sent())
        
        if acting_on == utils.TokenizeType.WORD_SENT:
            return self.break_contractions(self.tokenize_word_sent(True))

    def break_contractions(self, tokenized) -> list[str]:
        def break_logic(word, target):
            if not (
                word.endswith("'m") or \
                word.endswith("'re") or \
                word.endswith("n't") or \
                word.endswith("'s") or \
                word.endswith("'d")
            ):
                target.append(word)

            if word.endswith("'m"):
                target.extend(["I", "am"])
            if word.endswith("'re"):
                target.extend([word[:-3], "are"])
            if word.endswith("'d"):
                target.extend([word[:-2], "would"])
            if word.endswith("n't"):
                capitalize = word[0].isupper()
                broken = Tokenizer.CONTRACTIONS[word]
                broken[0] = broken[0].capitalize() if capitalize else broken[0].lower()
                target.extend(broken)
            if word.endswith("'s"):
                target.extend([word[:-2], "is"])
            return target

        result: list[str] = []
        if isinstance(tokenized[0], list):
            for sent in tokenized:
                result.append([])
                for word in sent:
                    result[-1] = break_logic(word, result[-1])
        else:
            for word in tokenized:
                result = break_logic(word, result)

        return result
        
    def remove_brackets(self):
        results = []
        for sent in self.text:
            results.append('')
            brackets = []
            for character in sent:
                if character in '([{':
                    brackets.append(character)

                if not brackets:
                    results[-1] += character

                if character in ')]}' and brackets:
                    brackets.pop()

            self.text = list(filter(lambda v:v, results))
        return self


