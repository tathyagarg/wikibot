import tokenizer as tokens
import lemmatizer as lemma

with open("corpus.txt", "r") as f:
    corpus = [line.strip() for line in f.readlines()]

token_maker = tokens.Tokenizer(corpus)
words = token_maker.tokenize_word_sent(punctuation=True)
broken = token_maker.break_contractions(words)
print(lemma.Lemmatizer(broken).tag_part_of_speech())
