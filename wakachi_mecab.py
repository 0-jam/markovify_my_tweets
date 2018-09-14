# 分かち書き用トークナイザ
import MeCab
m = MeCab.Tagger("-Owakati")

## 文sentenceを分かち書き
# Janomeと違い、解析結果がはじめからstrで返ってくるので、結合が必要ない
def divide_word(sentence):
    return m.parse(sentence).strip()

## 複数行の（iterableな）テキストtextを分かち書き
# 戻り値は行単位で要素に別れたlist
def divide_text(text):
    text = [divide_word(line) for line in text]
    # 入力テキストから空行を削除して返す
    return list(filter(lambda line: line != "", text))
