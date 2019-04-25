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

    def generate_sentence(self, gen_size=1):
        return self.model.make_sentence()

    def save(self, file_path):
        pass

    def load(self, file_path):
        pass
