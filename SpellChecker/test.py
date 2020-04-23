from spell_checker import SpellChecker

def main():
    checker = SpellChecker()
    sent = 'Matteo is my friend i hev no attencion sp'
    correction = checker.correct_sentence(sent)
    print(correction)



if __name__ == '__main__':
    main()


