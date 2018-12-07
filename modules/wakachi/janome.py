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
