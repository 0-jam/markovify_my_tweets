import MeCab
m = MeCab.Tagger("-Owakati")

## 文sentenceを分かち書き
def divide_word(sentence):
    sentence = sentence.strip()

    return m.parse(sentence).split()
