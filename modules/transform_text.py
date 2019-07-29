from pathlib import Path

from MeCab import Tagger

m = Tagger('-Ochasen')
stopwords = [line.strip() for line in Path('dict/stopwords_ja.txt').open()]


# Convert all Japanese conjugated words to the dictionary form（終止形）
def deconjugate_sentence(sentence):
    words = m.parse(sentence).splitlines()
    sentences = []

    for word in words:
        tags = word.split()

        if tags[0] == 'EOS':
            continue

        sentences.append(tags[2])

    return sentences


# Remove stopwords from a list of words (a sentence splitted by words)
def remove_stopwords(words):
    return [word for word in words if word not in stopwords]
