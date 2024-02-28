import lemmatizer as lemma
import tokenizer as token
from collections import defaultdict

class NGramMaker:
    def __init__(self, corpus: list[str]) -> None:
        self.corpus = corpus
        self.tokenizer = token.Tokenizer(text=corpus)
        self.words = self.tokenizer.tokenize_word_sent(punctuation=True)
        self.broken = self.tokenizer.break_contractions(tokenized=self.words)
        self.lemmatizer = lemma.Lemmatizer(text=self.broken)
        self.lemmas = self.lemmatizer.lemmatize()

        self.ngrams = {}

    def fetch_ngrams(self, n: int = 2):
        if not self.ngrams.get(n):
            self.ngrams[n] = {}
        for sentence in self.lemmas:
            # Using len-1 so that we don't run into an error when accessing element i+1
            for i in range(len(sentence)-1):
                curr = sentence[i]
                next_word = sentence[i+1]
                if not self.ngrams[n].get(curr):
                    self.ngrams[n][curr] = {}

                if not self.ngrams[n][curr].get(next_word):
                    self.ngrams[n][curr][next_word] = 0

                self.ngrams[n][curr][next_word] += 1
        
        return self.ngrams

