import constants as consts
import structures as structs


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
    def __init__(self, text: list[list[str]]) -> None:
        self.text = text

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
            word.pos = consts.POS.ADV
            return 0

        for wordset, corro in consts.DIRECT:
            if real_word in wordset:
                word.pos = corro
                return 0

        preceding = word.context[0]

        # Verbs
        if preceding.pos in (consts.POS.PRON, consts.POS.NOUN):
            word.pos = consts.POS.VERB
            return 0
        
        """
            Nouns and Adjectives

            PART A: Adjectives
                Check I: Preceding word is a determiner
                        Example: The tasty, Italian food is ...
                    1. When the program reaches 'tasty', it sees the previous word was a determiner.
                    2. It skips ahead over the list until it finds the first noun.
                    3. It then jumps back to tasty and counts the numbers of words from the determiner to the noun.
                    4. If the number is 0, the current word is a noun! Free noun identification as a side effect.
                    5. If the number is = 1, the current word is an adjective.
                    6. If the number is >= 2, a few of the following words are adjectives too, which may include particles like 'of' in 'few of'.
                Check II: Preceding word is a verb
                        Example: He only eats tasty food.
                    1. The program reaches 'tasty', and sees the preceding word is a verb.
                    2. The program then does the same steps as in Check I to find the adjectives.

            PART B: Nouns
                Word before a verb?
        """

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
        if preceding.pos == consts.POS.VERB:
            if real_word in consts.ADVERBS:
                word.pos = consts.POS.ADV
                word.context[1].pos = consts.POS.ADJ
                return 1
            else:
                word.pos = consts.POS.ADJ
                return 0

        word.pos = "Undetermined"
        return 0


    def tag_part_of_speech(self, sentence_idx: int = -1) -> list[list[tuple[str, consts.POS]]]:
        """
            The output of this function would be in the form:
            [ [ ( str, POS ) ] ]
            Xue Hua Piao Piao Bei Feng Xiao Xiao
        """
        target = self.extract_features(sentence_idx)
        skip = 0
        if sentence_idx == -1:
            for sentence in target:
                for idx, word in enumerate(sentence):
                    if skip > 0:
                        skip -= 1
                        continue
                    skip = self.classify(idx, sentence, word)
        else:
            for idx, word in enumerate(target):
                if skip > 0:
                    skip -= 1
                    continue
                skip = self.classify(idx, target, word)
        return target
    
    def extract_features(self, sentence_idx: int = -1) -> structs.Sentence | list[structs.Sentence]:
        result: list = []
        if sentence_idx == -1:
            # Disgusting O(n * m) time complexity, but I'm not going to think about it too hard.
            for sentence in self.text:
                result.append(make_sentence(sentence))
        else:
            result = make_sentence(self.text[sentence_idx])
        return result
