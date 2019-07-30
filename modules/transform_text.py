import re

from pathlib import Path

from MeCab import Tagger

m = Tagger('-Ochasen')
stopwords = [line.strip() for line in Path('dict/stopwords_ja.txt').open()]


# Convert all Japanese conjugated words to the dictionary form（終止形）
def deconjugate_sentence(sentence):
    # Remove EOS
    words = m.parse(sentence).splitlines()[:-1]
    sentences = []

    for word in words:
        tags = word.split()

        sentences.append(tags[2])

    return sentences


# Remove stopwords from a list of words (a sentence splitted by words)
def remove_stopwords(words):
    return [word for word in words if word not in stopwords]


def extract_nouns(sentence):
    words = [word.split() for word in m.parse(sentence).splitlines()][:-1]

    return [word[0] for word in words if re.search('名詞', word[3])]
