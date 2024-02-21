import tokenizer as tkzr

with open("corpus.txt", "r") as f:
    corpus = [line.strip() for line in f.readlines()]

token_maker = tkzr.Tokenizer(corpus)
print(token_maker.tokenize_punc_sent())
