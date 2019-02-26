from janome.tokenizer import Tokenizer
t = Tokenizer(wakati=True)

## 文sentenceを分かち書き
def divide_word(sentence):
    return list(filter(lambda line: line != ' ', t.tokenize(sentence.strip())))
