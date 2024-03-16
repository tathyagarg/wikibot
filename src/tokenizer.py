import re
import utils

def purify(text: list[str]) -> list[str]:
    """
        Removes empty strings
        
        :param text: The list to remove empty strings from
        :returns: The same list with None and empty string (or strings spaces) removed
    """
    return [i.strip() for i in text if i is not None and i.strip()]

class Tokenizer:
    CONTRACTIONS: dict[str, list[str]] = {
        "can't": ["can", "not"],
        "won't": ["will", "not"],
        "wouldn't": ["would", "not"],
        "shouldn't": ["should", "not"]
    }
    def __init__(self, text: str) -> None:
        self.text: list[str | list[str]] = text
        
    def tokenize_word(self, punctaution: bool = False, target: str = None) -> list[str]:
        """
            Tokenizes the string on words

            :param punctuation: Whether to include punctuation or not.
            :param target: The target of tokenizing. Defaults to `self.text`
            :returns: A list of words in the target, with or without punctuation depending on `punctuation` parameter
        """
        target: str = target or self.text
        pattern: str = r"[^\w']+" if not punctaution else r"\b[\w'-]+\b|\S"
        
        result: list[str] = re.findall(pattern, target)
        return purify(result)

    def tokenize_word_sent(self, punctuation: bool = False) -> list[list[str]]:
        """
            Tokenize self.text (which is a list of sentences) into words. Each sentence is tokenized into a separate list

            :param punctuation: Whether to include punctuation or not.
            :returns: A list of tokenized sentences
        """
        result: list[list[str]] = [self.tokenize_word(punctaution=punctuation, target=i) for i in self.text]
        return result
    
    def break_contractions_on(self, acting_on: utils.TokenizeType) -> list[list[str] | str]:
        """
            Breaks contractions after tokenizing on the given tokenize type

            :param acting_on: The tokenization type to break our text into
            :returns: A list[str | list[str]], depending on `acting_on`, with contractions such as "won't" broken into their constituent words
        """
        if acting_on == utils.TokenizeType.WORD:
            return self.break_contractions(self.tokenize_word(punctaution=True))
        
        if acting_on == utils.TokenizeType.WORD_SENT:
            return self.break_contractions(self.tokenize_word_sent(punctuation=True))

    def break_contractions(self, tokenized: list[list[str] | str]) -> list[str | list[str]]:
        """
            Break contractions on the given input

            :param tokenized: A list[str | list[str]], from which we replace contractions
            :returns: A list[str | list[str]], with replaced contractions
        """
        def break_logic(word: str, target: list[str]) -> list[str]:
            """
                Brain of the function. Does the actual replacing.

                :param word: Word to check for contractions
                :param target: List to which we append the processed word.
            """
            if not (
                word.endswith("'m") or \
                word.endswith("'re") or \
                word.endswith("n't") or \
                word.endswith("'s") or \
                word.endswith("'d")
            ):
                target.append(word)  # There are no contractions on this word.

            if word.endswith("'m"):
                target.extend(["I", "am"])
            elif word.endswith("'re"):
                target.extend([word[:-3], "are"])
            elif word.endswith("'d"):
                target.extend([word[:-2], "would"])
            elif word.endswith("n't"):
                capitalize = word[0].isupper()
                broken = Tokenizer.CONTRACTIONS[word]
                broken[0] = broken[0].capitalize() if capitalize else broken[0].lower()
                target.extend(broken)
            elif word.endswith("'s"):
                target.extend([word[:-2], "is"])

            return target

        result: list[str] = []
        if isinstance(tokenized[0], list):  # We have a list of list of strings as our input
            for sent in tokenized:
                result.append([])
                for word in sent:
                    result[-1] = break_logic(word, result[-1])
        else:  # We have a list of strings as our input
            for word in tokenized:
                result = break_logic(word, result)

        return result
        
    def remove_brackets(self):
        """
            Removes brackets from our text. Since this method is only invoked when we have multiple sentences (on our scraped corpus), we do not need to consider the possibility of self.text being a list[str], and only have to consider list[list[str]]
            Acts on un-tokenized data.

            :returns: self, with text modified to not have brackets.
        """
        results: list[str] = []
        for block in self.text:
            results.append('')
            brackets = []
            for character in block:
                if character in '([{':
                    brackets.append(character)

                if not brackets:
                    results[-1] += character

                if character in ')]}' and brackets:  # we don't have to verify bracket matching because it's extremely rare to find brackets like (] or {), etc.
                    brackets.pop()

            self.text: list[str] = list(filter(lambda v:v, results))
        return self


