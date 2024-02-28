import ngram

with open("corpus.txt", "r") as f:
    corpus = [line.strip() for line in f.readlines()]

print(ngram.NGramMaker(corpus=corpus).fetch_ngrams()[2])
