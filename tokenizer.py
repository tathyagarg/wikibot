import re

def purify(text: list[str]) -> list[str]:
    return [i.strip() for i in text if i.strip()]

class Tokenizer:
    def __init__(self, text: str | list[str]) -> None:
        self.text: str = text
        self.is_list = isinstance(text, list)
        self.action_text = [self.text, " ".join(self.text)][self.is_list]

    def tokenize_sent(self) -> list[str]:
        if self.is_list: return self.text
        result: list[str] = re.split(r'(?<=[.!?])', self.text)
        result = [sent.strip() for sent in result if sent.strip()]
        return result
    
    def tokenize_word(self, punctuation: bool = True) -> list[str]:
        pattern: str = r'\s+' if punctuation else r'\W+'

        result: list[str] = re.split(pattern, self.action_text)
        return purify(result)

    def tokenize_word_sent(self, punctuation: bool = True) -> list[list[str]]:
        result: list[str] = self.tokenize_sent()
        result = [Tokenizer(sent).tokenize_word(punctuation) for sent in result]
        return result
    
    def tokenize_punc_sent(self) -> list[list[str]]:
        result: list[str] = self.tokenize_sent()
        for (index, sent) in enumerate(result):
            result[index] = purify(re.split(r'(\W)', sent))
        return result

    def tokenize_punc(self) -> list[str]:
        result: list[str] = re.split(r'(\W)', self.action_text)
        return purify(result)
