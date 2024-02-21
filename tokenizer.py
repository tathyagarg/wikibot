import re

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
    
    def tokenize_word(self) -> list[str]:
        result: list[str] = re.split(r'\s+', self.action_text)
        return result

    def tokenize_word_sent(self) -> list[list[str]]:
        result: list[str] = self.tokenize_sent()
        result = [Tokenizer(sent).tokenize_word() for sent in result]
        return result
    
    def tokenize_punc_sent(self) -> list[list[str]]:
        result: list[str] = self.tokenize_sent()
        for (index, sent) in enumerate(result):
            result[index] = [i.strip() for i in re.split(r'(\W)', sent) if i.strip()]
        return result

    def tokenize_punc(self) -> list[str]:
        result: list[str] = [i.strip() for i in re.split(r'(\W)', self.action_text) if i.strip()]
        return result
