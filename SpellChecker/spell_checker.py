from enchant.checker import SpellChecker as SC

class SpellChecker:
    def __init__(self):
        self.checker = SC('en_US')

    def correct_sentence(self, sentence):
        checker = self.checker
        checker.set_text(sentence)
        for err in checker:
            if (err.word[0] != err.word[0].upper()):        # don't correct proper nouns
                correction = checker.suggest(err.word)[0]
                sentence = sentence.replace(err.word, correction)
        return sentence