from spell_checker import SpellChecker

def main():
    checker = SpellChecker()
    sent = 'Hello ther i em Philip'
    correction = checker.correct_sentence(sent)
    print(correction)



if __name__ == '__main__':
    main()


