import ngram
import tokenizer
import text_gen
import pos_tagger
import utils
import scraper
import query_analyzer
import data

analyzer = query_analyzer.RecurrentNeuralNetwork(10, 12, 1)
analyzer.train_test(data.DATA, data.DATA, min_time=0.75)

tagger = pos_tagger.Tagger()
info_fetcher = scraper.Scraper()

while True:
    tokens = tokenizer.Tokenizer(input('>>>')).break_contractions_on(utils.TokenizeType.WORD)

    tagged = utils.convert_tagged(tagger.tag(utils.make_words(tokens)))
    pos_only = [word.pos.value for word in tagged]

    pos_sent = utils.pad(pos_only, padding_character=-1, length=10)
    focus = query_analyzer.interpret_prediction(analyzer.predict(pos_sent), tagged)

    results = info_fetcher.fetch_results(str(focus))
    trigram_words = []
    for result in results:
        words = tokenizer.Tokenizer(result.split('.')).remove_brackets().break_contractions_on(utils.TokenizeType.WORD_SENT)
        words = list(filter(lambda v: v, words))
        for i in range(len(words)):
            words[i][0] = words[i][0].capitalize()
        trigram_words.extend(words)

    trigrams = ngram.Trigrams(utils.flatten(trigram_words))
    speaker = text_gen.TextGenerator(trigrams.first, trigrams.grams)
    speaker.speak_sentence()

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

