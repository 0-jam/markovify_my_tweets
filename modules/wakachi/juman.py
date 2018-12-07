from pyknp import Juman
juman = Juman()

## 文sentenceを分かち書き
# BUG: "ダブルクオーテーション"を含む文字列（'".'など）を投げるとその部分が二重になって返ってくる
def divide_word(sentence, delimiter=" "):
    sentence = sentence.strip()
    # Juman++に空文字列を投げると固まってしまう
    if not sentence:
        return sentence

    # テキストに半角スペースが含まれているとValueError: invalid literal for int() with base 10: '\\'で止まることがあるのでその対策
    # 半角スペースを全角スペースに置き換えている
    words = juman.analysis(sentence.replace(" ", "\u3000")).mrph_list()
    divided_sentence = [word.midasi for word in words]
    divided_sentence = list(filter(lambda line: line != "\u3000", divided_sentence))

    return delimiter.join(divided_sentence)
