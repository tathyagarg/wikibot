import ngram
import tokenizer
import lemmatizer
import text_gen

with open("corpus.txt", "r") as f:
    corpus = [line.strip() for line in f.readlines()]

tokenmaker = tokenizer.Tokenizer(text=corpus)
words = tokenmaker.tokenize_word_sent()
broken = tokenmaker.break_contractions(words)

lemmamaker = lemmatizer.Lemmatizer(text=broken)
lemmatized = lemmamaker.lemmatize()

bigrams = ngram.BigramMaker(lemmas=lemmatized).fetch_bigrams()

text_generator = text_gen.TextGenerator(bigrams=bigrams)
print(bigrams)
word = text_generator.speak_word('')

