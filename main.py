import ngram
import tokenizer
import text_gen
import pos_tagger
import constants as consts

with open("corpus.txt", "r") as f:
    corpus = [line.strip() for line in f.readlines()]

tokenmaker = tokenizer.Tokenizer(text=corpus)
words = tokenmaker.break_contractions_on(consts.TokenizeType.WORD_SENT)

tagger = pos_tagger.Tagger()
sentences = consts.make_sentences(words, tagger)

bigrams = ngram.BigramMaker(words=sentences).fetch_bigrams()
text_generator = text_gen.TextGenerator(bigrams=bigrams)

# This works too!
# text_generator = text_gen.TextGenerator(bigrams=ngram.BigramMaker(words=consts.make_sentences(tokenizer.Tokenizer(text=corpus).\
#     break_contractions_on(consts.TokenizeType.WORD_SENT), pos_tagger.Tagger())).fetch_bigrams())

word = consts.WordShell("his", consts.POS.ANY)

items = [word]
while True:
    try:
        items.append(text_generator.speak_from_word(items[-1])[1])
    except consts.CompleteSentence:
        break

sentence = consts.Sentence(items)
print(sentence.fix_syntax().joint())

