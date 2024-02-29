import constants as consts
import structures as structs
from collections import defaultdict


def make_sentence(sentence: list[str]) -> structs.Sentence:
    append_item = []
    word_index = 0
    for i, word in enumerate(sentence):
        if word in consts.PUNCTUATION:
            append_item.append(structs.Punctuation(word, i))
        else:
            append_item.append(structs.Word(word, word_index, i))
            word_index += 1
    return structs.Sentence(append_item)

class Lemmatizer:
    MORPHOLOGICAL_SUBSTITUTIONS = {
        consts.POS.NOUN: [
            ("s", ""),
            ("ses", "s"),
            ("ves", "f"),
            ("xes", "x"),
            ("zes", "z"),
            ("ches", "ch"),
            ("shes", "sh"),
            ("men", "man"),
            ("ies", "y"),
        ],
        consts.POS.VERB: [
            ("s", ""),
            ("ies", "y"),
            ("es", "e"),
            ("es", ""),
            ("ed", "e"),
            ("ed", ""),
            ("ing", "e"),
            ("ing", ""),
        ],
        consts.POS.ADJ: [("er", ""), ("est", ""), ("er", "e"), ("est", "e")],
        consts.POS.ADV: [],
    }

    def __init__(self, text: list[list[str]]) -> None:
        self.text = text
        self.exception_map: dict[consts.POS, dict[str, str]] = {}

        # Defaults to set a key to an empty dict if it is not already present
        self.lemma_pos_offset_map = defaultdict(dict)

        self.FILEMAP = {
            consts.POS.ADJ: "adj",
            consts.POS.ADV: "adv",
            consts.POS.NOUN: "noun",
            consts.POS.VERB: "verb",
            consts.POS.HELP: "verb"
        }

        self.LETTER_TO_POS = {
            "a": consts.POS.ADJ,
            "r": consts.POS.ADV,
            "n": consts.POS.NOUN,
            "v": consts.POS.VERB
        }

        self.load_exception_map()
        self.load_lemma_pos_offset_map()

    def open(self, fp: str):
        with open(fp, "r") as f:
            return list(map(str.rstrip, f.readlines()))

    def load_exception_map(self) -> None:
        for pos, text in self.FILEMAP.items():
            self.exception_map[pos] = {}
            for line in self.open(f"data/{text}.exc"):
                terms = line.split()
                self.exception_map[pos][terms[0]] = terms[1:]
    
    def load_lemma_pos_offset_map(self):
        for suffix in self.FILEMAP.values():
            for line in self.open(f"data/index.{suffix}"):
                # Ignore comment
                if line.startswith(" "):
                    continue

                _iter = iter(line.split())

                def _next_token():
                    return next(_iter)

                lemma = _next_token()
                pos = self.LETTER_TO_POS[_next_token()]
                n_synsets = int(_next_token())
                n_pointers = int(_next_token())
                # Skip next tokens
                [_next_token() for _ in range(n_pointers+2)]

                synset_offsets = [int(_next_token()) for _ in range(n_synsets)]

                self.lemma_pos_offset_map[lemma][pos] = synset_offsets
    
    def make_lemma(self, word: str, pos: consts.POS) -> str:
        # The code here will be almost a 1-to-1 copy of the code form nltk.corpus.WordNetCorpusReader
        # It will be modified to fit this environment
        exceptions = self.exception_map[pos]
        substitutions = self.MORPHOLOGICAL_SUBSTITUTIONS[pos]

        def apply_rules(forms):
            return [
                form[:-len(old)] + new
                for form in forms
                for old, new in substitutions
                if form.endswith(old)
            ]

        def filter_forms(forms):
            result = []
            seen = set()
            for form in forms:
                if form in self.lemma_pos_offset_map:
                    if pos in self.lemma_pos_offset_map[form]:
                        if form not in seen:
                            result.append(form)
                            seen.add(form)
            return result

        if word in exceptions:
            return filter_forms([word] + exceptions[word])

        forms = apply_rules([word])

        results = filter_forms([word] + forms)
        if results:
            return results

        while forms:
            forms = apply_rules(forms)
            results = filter_forms(forms)
            if results:
                return results

        return []


    def classify(self, idx: int, sentence: structs.Sentence, word: structs.Word) -> int:
        """
        Function that classifies the given word into a part of speech.
        Return:
            int (a)
        (a) - The number of iterations to skip

        @idx: int - The current index
        @sentence: list[dict] - The sentence being parsed
        @word: dict - The features of the word being parsed

        English is too complex to make a pattern :(
        """
        if isinstance(word, structs.Punctuation):
            word.pos = consts.POS.PUNC
            return 0
    
        real_word = word.word.lower()

        if word.index == 0 and real_word in consts.INTERROGATIVE_ADV:
            word.pos = consts.POS.INTR
            return 0

        for wordset, corro in consts.DIRECT:
            if real_word in wordset:
                word.pos = corro
                return 0

        preceding = word.context[0]
        proceding = word.context[1]

        if real_word == "all" and proceding.word.lower() == "of":
            word.pos = consts.POS.QUAN
            proceding.pos = consts.POS.PREP
            return 1

        # Verbs
        if preceding.pos in (consts.POS.PRON, consts.POS.NOUN, consts.POS.INTR):
            word.pos = consts.POS.VERB
            return 0

        if preceding.pos in (consts.POS.POS, consts.POS.ART):
            if real_word in consts.NOUNS or word.capitalization:
                # Checks if the word is a noun, or is capitalized ^^^^.
                word.pos = consts.POS.NOUN
                return 0
            # else:
            for index, new_word in enumerate(sentence[idx:], idx):
                if isinstance(new_word, structs.Punctuation):
                    new_word.pos = consts.POS.PUNC
                elif new_word.word in consts.NOUNS:
                    displacement = index-idx
                    new_word.pos = consts.POS.NOUN
                    return displacement
                else:
                    new_word.pos = consts.POS.ADJ

        """
            This works because if the sentence was:
                He is a happy boy
            The code would catch 'a' earlier when searching for articles
            It only catches adverbs and adjectives
            Wonder if we can catch adverbs earlier, though. Doubt it.
        """
        if preceding.pos == consts.POS.HELP:
            if real_word in consts.ADVERBS:
                word.pos = consts.POS.ADV
                proceding.pos = consts.POS.VERB
                return 1
            else:
                word.pos = consts.POS.VERB
                return 0
            

        if preceding.pos == consts.POS.VERB:
            if real_word in consts.PREPOSITIONS:
                word.pos = consts.POS.PREP
                return 0
            elif real_word in consts.ADVERBS:
                word.pos = consts.POS.ADV
                proceding.pos = consts.POS.ADJ
                return 1
            else:
                if not proceding:
                    word.pos = consts.POS.NOUN
                    return 0
                word.pos = consts.POS.ADJ
                if proceding.word.lower() in consts.PREPOSITIONS:
                    proceding.pos = consts.POS.PREP
                return 1

        print('='*30+f'Undetermined {word} on {sentence}'+'='*30)
        word.pos = "Undetermined"
        return 0


    def fetch_pos(self) -> list[list[tuple[str, consts.POS]]]:
        """
            The output of this function would be in the form:
            [ [ ( str, POS ) ] ]
            Xue Hua Piao Piao Bei Feng Xiao Xiao
        """
        target = self.extract_features()
        skip = 0
        for sentence in target:
            for idx, word in enumerate(sentence):
                if skip > 0:
                    skip -= 1
                    continue
                skip = self.classify(idx, sentence, word)

        # Post-classification
        for sentence in target:
            for word in sentence:
                if word.pos == consts.POS.HELP: word.pos = consts.POS.VERB

        return target
    
    def extract_features(self) -> list[structs.Sentence]:
        result: list = [
            make_sentence(sentence) for sentence in self.text
        ]
        return result

    def lemmatize(self) -> list[list[structs.WordShell]]:
        result = []
        for sentence in self.fetch_pos():
            print(f"Sentence: {sentence}")
            result.append([])
            for word in sentence:
                if isinstance(word, structs.Punctuation):
                    continue
                elif word.pos in (consts.POS.ADJ, consts.POS.ADV, consts.POS.VERB, consts.POS.NOUN):
                    if (lemma := self.make_lemma(word.word, word.pos)):
                        result[-1].extend(list(map(str.lower, lemma)))
                    else:
                        result[-1].append(word.word.lower())
                else:
                    result[-1].append(word.word.lower())
        return result
    