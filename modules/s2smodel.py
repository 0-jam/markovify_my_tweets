import functools

from tensorflow import keras

from modules.text_model import TextModel


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
        encoder = keras.layers.Embedding(self.vocab_size, self.embedding_dim)(enc_in)
        encoder, state_h, state_c = lstm(return_state=True)(encoder)
        enc_states = [state_h, state_c]

        # Decoder layers
        dec_in = keras.layers.Input(shape=(None,))
        decoder = keras.layers.Embedding(self.vocab_size, self.embedding_dim)(dec_in)
        decoder = lstm()(decoder, initial_state=enc_states)
        dec_out = keras.layers.Dense(self.vocab_size, activation='softmax')(decoder)

        return keras.Model([enc_in, dec_in], dec_out)
