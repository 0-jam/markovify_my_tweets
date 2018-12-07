import MeCab
m = MeCab.Tagger("-Owakati")

## 文sentenceを分かち書き
# Janomeと違い，解析結果がはじめからstrで返ってくるので，結合が必要ない
def divide_word(sentence):
    return m.parse(sentence).strip()
