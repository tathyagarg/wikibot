import tokenizer as tokens
import lemmatizer as lemma
import constants as consts

with open("corpus.txt", "r") as f:
    corpus = [line.strip() for line in f.readlines()]

token_maker = tokens.Tokenizer(corpus)
words = token_maker.tokenize_word_sent(punctuation=True)
broken = token_maker.break_contractions(words)

# for sent in lemma.Lemmatizer(broken).fetch_pos():
#     for word in sent:
#         print(f"{word}: {word.pos}", end=" ; ")
#     print()
print(lemma.Lemmatizer(broken).lemmatize())

