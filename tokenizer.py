import re
import constants as consts

def purify(text: list[str]) -> list[str]:
    return [i.strip() for i in text if i is not None and i.strip()]

class Tokenizer:
    CONTRACTIONS = {
        "can't": ["can", "not"],
        "won't": ["will", "not"],
        "wouldn't": ["would", "not"],
        "shouldn't": ["should", "not"]
    }
    def __init__(self, text: str | list[str]) -> None:
        self.text: str = text
        
    def tokenize_word(self, sentence_idx: int = 0, punctaution: bool = False) -> list[str]:
        pattern: str = r"[^\w']+" if not punctaution else r"\b[\w'-]+\b|\S"

        result: list[str] = re.findall(pattern, self.text[sentence_idx])
        return purify(result)

    def tokenize_word_sent(self, punctuation: bool = False) -> list[list[str]]:
        result = [self.tokenize_word(i, punctaution=punctuation) for i in range(len(self.text))]
        return result
    
    def tokenize_punc_sent(self) -> list[list[str]]:
        result = self.text[:]
        for (index, sent) in enumerate(result):
            result[index] = purify(re.split(r'(\W)', sent))
        return result
    
    def break_contractions_on(self, acting_on: consts.TokenizeType) -> list[str]:
        if acting_on == consts.TokenizeType.WORD:
            return self.break_contractions(self.tokenize_word())
        
        if acting_on == consts.TokenizeType.PUNC_SENT:
            return self.break_contractions(self.tokenize_punc_sent())
        
        if acting_on == consts.TokenizeType.WORD_SENT:
            return self.break_contractions(self.tokenize_word_sent(True))

    def break_contractions(self, tokenized) -> list[str]:
        result: list[list[str]] = []
        for sentence in tokenized:
            result.append([])
            for word in sentence:
                if not (
                    word.endswith("'m") or \
                    word.endswith("'re") or \
                    word.endswith("n't") or \
                    word.endswith("'s") or \
                    word.endswith("'d")
                ):
                    result[-1].append(word)

                if word.endswith("'m"):
                    result[-1].extend(["I", "am"])
                if word.endswith("'re"):
                    result[-1].extend([word[:-3], "are"])
                if word.endswith("'d"):
                    result[-1].extend([word[:-2], "would"])
                if word.endswith("n't"):
                    capitalize = word[0].isupper()
                    broken = Tokenizer.CONTRACTIONS[word]
                    broken[0] = broken[0].capitalize() if capitalize else broken[0].lower()
                    result[-1].extend(broken)
                if word.endswith("'s"):
                    result[-1].extend([word[:-2], "is"])
                
        return result
