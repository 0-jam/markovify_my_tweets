# 分かち書き用トークナイザ
from janome.tokenizer import Tokenizer
t = Tokenizer(wakati=True)

## 文sentenceを分かち書き
# delimiter（デフォルトは半角スペース）で単語どうしをつなぐ
def divide_word(sentence, delimiter=" "):
    return delimiter.join(
        list(filter(
            lambda line: line != " ", t.tokenize(sentence.strip())
        ))
    )

## 複数行の（iterableな）テキストtextを分かち書き
# 戻り値は行単位で要素に別れたlist
def divide_text(text, delimiter=" "):
    text = [divide_word(line, delimiter=delimiter) for line in text]
    # 入力テキストから空行を削除して返す
    return list(filter(lambda line: line != "", text))
