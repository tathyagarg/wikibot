import ngram
import tokenizer
import lemmatizer
import text_gen
import pos_tagger

with open("corpus.txt", "r") as f:
    corpus = [line.strip() for line in f.readlines()]

tokenmaker = tokenizer.Tokenizer(text=corpus)
words = tokenmaker.tokenize_word_sent()
broken = tokenmaker.break_contractions(words)

tagger = pos_tagger.Tagger(tokenizer=tokenmaker)

lemmamaker = lemmatizer.Lemmatizer(text=broken, tagger=tagger)
lemmatized = lemmamaker.lemmatize()

bigrams = ngram.BigramMaker(lemmas=lemmatized).fetch_bigrams()

text_generator = text_gen.TextGenerator(bigrams=bigrams)
print(bigrams)

word = 'his'

while word in bigrams:
    print(word)
    word = text_generator.speak_word(word)
print(word)
