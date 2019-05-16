from pathlib import Path

import markovify

from modules.wakachi.mecab import divide_word


# Markov chain based model
class MCModel(object):
    def __init__(self):
        self.model = None
        self.dataset = None

    def build_dataset(self, text_path, char_level=False, encoding='utf-8'):
        with Path(text_path).open(encoding=encoding) as text_fp:
            text = text_fp.read().strip().split('\n')

        if not char_level:
            text = [' '.join(divide_word(line)) for line in text]
        else:
            text = [' '.join(line) for line in text]

        self.dataset = '\n'.join(text)

    def build_model(self, states=2):
        self.model = markovify.NewlineText(self.dataset)

    def save_model(self, file_path):
        with Path(file_path).open('w', encoding='utf-8') as out:
            out.write(self.model.to_json())

    def load_model(self, file_path):
        with Path(file_path).open(encoding='utf-8') as input:
            self.model = markovify.NewlineText.from_json(input.read())

    def generate_sentence(self, gen_size=None):
        if gen_size is None:
            generated_sentence = self.model.make_sentence()
        else:
            print('short_sentence mode')
            generated_sentence = self.model.make_short_sentence(gen_size)

        return generated_sentence
