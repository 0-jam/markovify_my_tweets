from janome.tokenizer import Tokenizer

t = Tokenizer(wakati=True)


# Split sentence by word
def divide_word(sentence):
    return list(filter(lambda line: line != ' ', t.tokenize(sentence.strip())))
