import MeCab
m = MeCab.Tagger('-Owakati')

## 文sentenceを分かち書き
def divide_word(sentence):
    return m.parse(sentence.strip()).split()
