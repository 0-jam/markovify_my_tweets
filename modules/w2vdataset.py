from modules.wakachi.mecab import divide_word
from modules.dataset import TextDataset

class W2VDataset(TextDataset):
    def __init__(self, text, batch_size):
        # unique word in text
        words = text.split()
        super(W2VDataset, self).__init__(words, batch_size)

    ## Convert word to numbers
    def vocab_to_indices(self, words):
        if type(words) == str:
            words = divide_word(words)

        return [self.vocab2idx[word] for word in words]
