import ngram
import tokenizer
import text_gen
import pos_tagger
import utils
import scraper
import query_analyzer
import data

tokens = tokenizer.Tokenizer(text=['What is ice-cream 2']).break_contractions_on(utils.TokenizeType.WORD_SENT)

tagged = utils.convert_tagged(pos_tagger.Tagger().tag(utils.make_words(tokens)))
pos_only = [[word.pos.value for word in sent] for sent in tagged]

analyzer = query_analyzer.RecurrentNeuralNetwork(10, 12, 1)
analyzer.train_on(data.DATA, min_time=0.5)

for sent in pos_only:
    sent = utils.pad(sent, padding_character=-1, length=10)
    print(sent)
    print(analyzer.predict(sent))

# _scraper = scraper.Scraper()
# print(_scraper.fetch_results('ice-cream'))

# tokens = tokenizer.Tokenizer(text=["What is ice-cream?"]).break_contractions_on(utils.TokenizeType.WORD_SENT)
# tagger = pos_tagger.Tagger()
# sentences = utils.make_sentences(tokens, tagger)

#question_parser.get_active_term(sentences[0])

# with open(utils.CORPUS_LOCATION, "r") as f:
#     corpus = [line.strip() for line in f.readlines()]

# tokenmaker = tokenizer.Tokenizer(text=corpus)
# words = tokenmaker.break_contractions_on(utils.TokenizeType.WORD_SENT)

# tagger = pos_tagger.Tagger()
# sentences = utils.make_sentences(words, tagger)

# bigrams = ngram.BigramMaker(words=sentences).fetch_bigrams()
# text_generator = text_gen.TextGenerator(bigrams=bigrams)

# # This works too!
# # text_generator = text_gen.TextGenerator(bigrams=ngram.BigramMaker(words=utils.make_sentences(tokenizer.Tokenizer(text=corpus).\
# #     break_contractions_on(utils.TokenizeType.WORD_SENT), pos_tagger.Tagger())).fetch_bigrams())

# word = utils.WordShell("his", utils.POS.ANY)

# items = [word]
# while True:
#     try:
#         items.append(text_generator.speak_from_word(items[-1])[1])
#     except utils.CompleteSentence:
#         break

# sentence = utils.Sentence(items)
# print(sentence.fix_syntax().joint())

