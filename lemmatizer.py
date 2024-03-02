import constants as consts
import structures as structs
from collections import defaultdict


def make_sentence(sentence: list[str]) -> structs.Sentence:
    append_item = []
    word_index = 0
    for i, word in enumerate(sentence):
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
        consts.POS.ADJECTIVE: [("er", ""), ("est", ""), ("er", "e"), ("est", "e")],
        consts.POS.ADVERB: [],
    }

    FILEMAP = {
        consts.POS.ADJECTIVE: "adj",
        consts.POS.ADVERB: "adv",
        consts.POS.NOUN: "noun",
        consts.POS.VERB: "verb"
    }

    LETTER_TO_POS = {
        "a": consts.POS.ADJECTIVE,
        "r": consts.POS.ADVERB,
        "n": consts.POS.NOUN,
        "v": consts.POS.VERB
    }

    STR_TO_POS = {
        'CC': consts.POS.CONJUNCTION,
        'CD': consts.POS.CARDINAL,
        'DT': consts.POS.DETERMINER,
        'EX': consts.POS.EXISTANCE_THERE,
        'FW': consts.POS.FOREIGN,
        'IN': consts.POS.PREPOSITION,
        'JJ': consts.POS.ADJECTIVE, 'JJR': consts.POS.ADJECTIVE, 'JJS': consts.POS.ADJECTIVE,
        'LS': consts.POS.LIST_MARKER,
        'MD': consts.POS.MODAL,
        'NN': consts.POS.NOUN, 'NNS': consts.POS.NOUN, 'NNP': consts.POS.NOUN, 'NNPS': consts.POS.NOUN,
        'PDT': consts.POS.PREDETERMINER,
        'POS': consts.POS.POSSESSIVE_ENDING,
        'PRP': consts.POS.PRONOUN, 'PRP$': consts.POS.PRONOUN,
        'RB': consts.POS.ADVERB, 'RBR': consts.POS.ADVERB, 'RBS': consts.POS.ADVERB,
        'RP': consts.POS.PARTICLE,
        'SYM': consts.POS.SYMBOL,
        'TO': consts.POS.TO,
        'UH': consts.POS.INTERJECTION,
        'VB': consts.POS.VERB, 'VBD': consts.POS.VERB, 'VBG': consts.POS.VERB, 'VBN': consts.POS.VERB, 'VBP': consts.POS.VERB, 'VBZ': consts.POS.VERB,
        'WDT': consts.POS.WH_DETERMINER,
        'WP': consts.POS.WH_PRONOUN,
        'WP$': consts.POS.POSSESSIVE_WH,
        'WRB': consts.POS.WH_ADVERB
    }

    def __init__(self, text: list[list[str]], tagger) -> None:
        self.text = text
        self.exception_map: dict[consts.POS, dict[str, str]] = {}
        self.tagger = tagger

        # Defaults to set a key to an empty dict if it is not already present
        self.lemma_pos_offset_map = defaultdict(dict)

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


    def classify(self, sentence: structs.Sentence) -> int:
        tagged = self.tagger.tag(sentence)
        result = []
        for (word, pos) in tagged:
            result.append((word, self.__class__.STR_TO_POS[pos]))

        return result


    def fetch_pos(self) -> list[list[tuple[str, consts.POS]]]:
        """
            The output of this function would be in the form:
            [ [ ( str, POS ) ] ]
            Xue Hua Piao Piao Bei Feng Xiao Xiao
        """
        result = []
        target = self.extract_features()
        for sentence in target:

            result.append(self.classify(sentence))

        return result

    def extract_features(self) -> list[structs.Sentence]:
        result: list = [
            make_sentence(sentence) for sentence in self.text
        ]
        return result

    def lemmatize(self) -> list[list[structs.WordShell]]:
        result = []
        parts_of_speech = self.fetch_pos()
        for sentence in parts_of_speech:
            result.append([])
            for word in sentence:
                if word[1] in (consts.POS.ADJECTIVE, consts.POS.ADVERB, consts.POS.VERB, consts.POS.NOUN):
                    if (lemma := self.make_lemma(*word)):
                        result[-1].extend(list(map(str.lower, lemma)))
                    else:
                        result[-1].append(word[0].lower())
                else:
                    result[-1].append(word[0].lower())
        return result
    