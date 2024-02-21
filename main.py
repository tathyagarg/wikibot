import tokenizer as tokens
import lemmatizer as lemma

with open("corpus.txt", "r") as f:
    corpus = [line.strip() for line in f.readlines()]

token_maker = tokens.Tokenizer(corpus)
words = token_maker.tokenize_word_sent(False)
print(lemma.Lemmatizer(words).extract_features())
