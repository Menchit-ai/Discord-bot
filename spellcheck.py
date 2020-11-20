from spellchecker import SpellChecker
import json

with open('./data_characters/pilote.json','r') as json_file:
    data = json.load(json_file)
    keys = data.keys()
    spell = SpellChecker(language=None)
    spell.word_frequency.load_words(keys)

    word = 'pliotaeg'

    print(spell.word_probability(word))
    print(spell.correction(word))