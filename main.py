import ngram
import tokenizer
import text_gen
import pos_tagger
import utils

with open(utils.CORPUS_LOCATION, "r") as f:
    corpus = [line.strip() for line in f.readlines()]

tokenmaker = tokenizer.Tokenizer(text=corpus)
words = tokenmaker.break_contractions_on(utils.TokenizeType.WORD_SENT)

tagger = pos_tagger.Tagger()
sentences = utils.make_sentences(words, tagger)

bigrams = ngram.BigramMaker(words=sentences).fetch_bigrams()
text_generator = text_gen.TextGenerator(bigrams=bigrams)

# This works too!
# text_generator = text_gen.TextGenerator(bigrams=ngram.BigramMaker(words=utils.make_sentences(tokenizer.Tokenizer(text=corpus).\
#     break_contractions_on(utils.TokenizeType.WORD_SENT), pos_tagger.Tagger())).fetch_bigrams())

word = utils.WordShell("his", utils.POS.ANY)

items = [word]
while True:
    try:
        items.append(text_generator.speak_from_word(items[-1])[1])
    except utils.CompleteSentence:
        break

sentence = utils.Sentence(items)
print(sentence.fix_syntax().joint())

