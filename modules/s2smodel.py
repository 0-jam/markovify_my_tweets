from modules.model import TextModel
from tensorflow import keras
import functools
import time

# Character-based Seq2seq model
class S2SModel(TextModel):
    def build_model(self):
        # Disable CUDA if GPU is not available
        if self.cpu_mode:
            lstm = functools.partial(
                keras.layers.LSTM,
                self.units,
                return_sequences=True,
                recurrent_activation='sigmoid',
                recurrent_initializer='glorot_uniform'
            )
        else:
            lstm = functools.partial(
                keras.layers.CuDNNLSTM,
                self.units,
                return_sequences=True,
                recurrent_initializer='glorot_uniform'
            )

        # Encoder layers
        enc_in = keras.layers.Input(shape=(None,))
        enc_emb = keras.layers.Embedding(self.vocab_size, self.embedding_dim)(enc_in)
        enc_lstm, state_h, state_c = lstm(return_state=True)(enc_emb)
        enc_states = [state_h, state_c]

        # Decoder layers
        dec_in = keras.layers.Input(shape=(None,))
        dec_emb = keras.layers.Embedding(self.vocab_size, self.embedding_dim)(dec_in)
        dec_lstm = lstm()(dec_emb, initial_state=enc_states)
        dec_dense = keras.layers.Dense(self.vocab_size, activation='softmax')(enc_lstm)

        return keras.Model([enc_in, dec_in], dec_dense)
