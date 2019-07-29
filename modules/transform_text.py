from MeCab import Tagger

m = Tagger('-Ochasen')


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
