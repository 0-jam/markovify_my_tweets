import tensorflow as tf
import numpy as np
from pathlib import Path

class TextDataset():
    def __init__(self, text, batch_size, use_dict=False):
        ## Vectorize the text
        if use_dict:
            text + self.dict()
        # unique character in text
        vocab = sorted(set(text))
        self.vocab_size = len(vocab)
        print("Text has {} characters ({} unique characters)".format(len(text), self.vocab_size))
        # Creating a mapping from unique characters to indices
        # This list doesn't have character that is not contained in the text
        self.vocab2idx = {char:index for index, char in enumerate(vocab)}
        self.idx2vocab = np.array(vocab)
        text_as_int = np.array(self.vocab_to_indices(text))

        # The maximum length sentence we want for single input in characters
        seq_length = 100
        chunks = tf.data.Dataset.from_tensor_slices(text_as_int).batch(seq_length + 1, drop_remainder=True)

        self.batch_size = batch_size
        # Buffer size to shuffle the dataset
        buffer_size = 10000

        ## Creating batches and shuffling them
        dataset = chunks.map(self.split_into_target)
        self.dataset = dataset.shuffle(buffer_size).batch(self.batch_size, drop_remainder=True)

    ## Create input and target texts from the text
    @staticmethod
    def split_into_target(chunk):
        input_text = chunk[:-1]
        target_text = chunk[1:]

        return input_text, target_text

    ## Convert string to numbers
    def vocab_to_indices(self, str):
        return [self.vocab2idx[c] for c in str]

    ## Load dictionary data
    @staticmethod
    def dict():
        dicts = ''
        for dic in Path("dict").iterdir():
            dicts += dic.open(encoding='utf-8').read()

        return dicts
