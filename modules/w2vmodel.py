import multiprocessing as mp
import re
import time

import numpy as np
import tensorflow as tf
from gensim.models import Word2Vec
from tensorflow import keras
from tqdm import tqdm

from modules.model import TextModel
from modules.wakachi.mecab import divide_word

MAX_SENTENCE_LEN = 500
NUM_CPU = mp.cpu_count()


# Word2vec model
class W2VModel(TextModel):
    def __init__(self, embedding_dim, units, batch_size, text, cpu_mode=True, w2vmodel=None):
        sentences = [line.split()[:MAX_SENTENCE_LEN] for line in text]

        if w2vmodel:
            print('Loading word2vec model ...')
            self.w2vmodel = Word2Vec.load(str(w2vmodel))
        else:
            print('Generating word2vec model ...')
            self.w2vmodel = Word2Vec(sentences, size=embedding_dim, min_count=1, window=5, iter=100, workers=NUM_CPU)

        self.w2vweights = self.w2vmodel.wv.syn0
        self.vocab_size, self.embedding_dim = self.w2vweights.shape
        print("Text has {} unique words".format(self.vocab_size))

        self._train_x, self._train_y = self.text2idxs(sentences)

        self.units = units
        self.batch_size = batch_size
        self.cpu_mode = not tf.test.is_gpu_available() or cpu_mode
        self.model = self.build_model()

    def build_model(self):
        # Disable CUDA if GPU is not available
        if self.cpu_mode:
            gru = keras.layers.GRU(
                self.units,
                recurrent_activation='sigmoid',
                recurrent_initializer='glorot_uniform'
            )
        else:
            gru = keras.layers.CuDNNGRU(
                self.units,
                recurrent_initializer='glorot_uniform'
            )

        return keras.Sequential([
            keras.layers.Embedding(self.vocab_size, self.embedding_dim, weights=[self.w2vweights]),
            gru,
            keras.layers.Dropout(0.5),
            keras.layers.Dense(self.vocab_size),
        ])

    def fit(self, model_dir, epochs):
        checkpoint_callback = keras.callbacks.ModelCheckpoint(str(model_dir.joinpath("ckpt_{epoch}")), save_weights_only=True, period=5, verbose=1)
        earlystop_callback = keras.callbacks.EarlyStopping(monitor='loss', patience=4, verbose=1)

        start_time = time.time()
        history = self.model.fit(self._train_x, self._train_y, batch_size=self.batch_size, epochs=epochs, callbacks=[checkpoint_callback, earlystop_callback])
        elapsed_time = time.time() - start_time
        print("Time taken for learning {} epochs: {:.3f} minutes ({:.3f} minutes / epoch )".format(epochs, elapsed_time / 60, (elapsed_time / epochs) / 60))

        return history

    def save(self, model_dir):
        super().save(model_dir)
        self.w2vmodel.save(str(model_dir.joinpath("w2v.model")))

    def generate_text(self, start_string, gen_size=1, temp=1.0):
        generated_text = [start_string]
        # Vectorize start_string
        try:
            input_eval = tf.expand_dims([self.vocab2idx(word) for word in divide_word(start_string)], 0)
            print('Start string:', start_string)
        except KeyError:
            print('Unknown word included')
            return ''

        # Randomness of text generation
        temperature = temp

        count = 0
        self.model.reset_states()
        with tqdm(desc='Generating...', total=gen_size) as pbar:
            while count < gen_size:
                predictions = self.model(input_eval)
                # remove the batch dimension
                predictions = tf.squeeze(predictions, 0)

                # Using the multinomial distribution to predict the word returned by the model
                predictions = predictions / temperature
                predicted_id = tf.multinomial([predictions], num_samples=1)[-1, 0].numpy()

                # Pass the predicted word as the next input to the model along with the previous hidden state
                input_eval = tf.expand_dims([predicted_id], 0)

                generated_text.append(self.idx2vocab(predicted_id))

                count += 1
                pbar.update()

        return generated_text

    # Vectorize the text
    def text2idxs(self, sentences):
        train_x = np.zeros([len(sentences), MAX_SENTENCE_LEN], dtype=np.int32)
        train_y = np.zeros([len(sentences)], dtype=np.int32)
        for i, sentence in enumerate(sentences):
            for t, word in enumerate(sentence[:-1]):
                train_x[i, t] = self.vocab2idx(word)
            train_y[i] = self.vocab2idx(sentence[-1])

        return train_x, train_y

    def vocab2idx(self, vocab):
        return self.w2vmodel.wv.vocab[vocab].index

    def idx2vocab(self, idx):
        return self.w2vmodel.wv.index2word[idx]
