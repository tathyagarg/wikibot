import ngram
import tokenizer
import lemmatizer
import text_gen
import pos_tagger
import constants as consts

with open("corpus.txt", "r") as f:
    corpus = [line.strip() for line in f.readlines()]

tokenmaker = tokenizer.Tokenizer(text=corpus)
words = tokenmaker.break_contractions_on(consts.TokenizeType.WORD_SENT)

tagger = pos_tagger.Tagger(tokenizer=tokenmaker)

lemmamaker = lemmatizer.Lemmatizer(text=words, tagger=tagger)
lemmatized = lemmamaker.lemmatize()

bigrams = ngram.BigramMaker(lemmas=lemmatized).fetch_bigrams()

text_generator = text_gen.TextGenerator(bigrams=bigrams)

word = consts.WordShell("his", consts.POS.ANY)

print(word in bigrams)

while consts.word_exists_in(word, bigrams):
    print(word)
    word = text_generator.speak_from_word(word)
print(word)
