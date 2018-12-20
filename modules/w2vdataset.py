import tensorflow as tf
import numpy as np
from pathlib import Path
from modules.wakachi.mecab import divide_word
from modules.dataset import TextDataset

class W2VDataset(TextDataset):
    def __init__(self, text, batch_size):
        # unique word in text
        words = text.split()
        vocab = sorted(set(words))
        self.vocab_size = len(vocab)
        print("Text has {} words ({} unique words)".format(len(words), self.vocab_size))
        # Creating a mapping from unique words to indices
        # This list doesn't have word that is not contained in the text
        self.vocab2idx = {word:index for index, word in enumerate(vocab)}
        self.idx2vocab = np.array(vocab)
        word_as_int = np.array(self.vocab_to_indices(words))

        # The maximum length sentence we want for single input in words
        seq_length = 100
        chunks = tf.data.Dataset.from_tensor_slices(word_as_int).batch(seq_length + 1, drop_remainder=True)

        self.batch_size = batch_size
        # Buffer size to shuffle the dataset
        buffer_size = 10000

        ## Creating batches and shuffling them
        dataset = chunks.map(self.split_into_target)
        self.dataset = dataset.shuffle(buffer_size).batch(self.batch_size, drop_remainder=True)

    ## Convert word to numbers
    def vocab_to_indices(self, words):
        if type(words) == str:
            words = divide_word(words)

        return [self.vocab2idx[word] for word in words]
