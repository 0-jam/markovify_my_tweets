import tensorflow as tf
from tensorflow import keras
from pathlib import Path
import json
from tqdm import tqdm
import time

## Keras Functional API implementation
class Model(object):
    def __init__(self, vocab_size, embedding_dim, units, batch_size, cpu_mode=False):
        # Hyper parameters
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.units = units
        self.batch_size = batch_size
        self.cpu_mode = not tf.test.is_gpu_available() or cpu_mode

        self.model = self.build_model()

    def build_model(self):
        # Disable CUDA if GPU is not available
        if not self.cpu_mode:
            gru = keras.layers.GRU(
                self.units,
                return_sequences=True,
                stateful=True,
                recurrent_activation='sigmoid',
                recurrent_initializer='glorot_uniform'
            )
        else:
            gru = keras.layers.CuDNNGRU(
                self.units,
                return_sequences=True,
                stateful=True,
                recurrent_activation='sigmoid',
                recurrent_initializer='glorot_uniform'
            )

        return keras.Sequential([
            keras.layers.Embedding(self.vocab_size, self.embedding_dim, batch_input_shape=[self.batch_size, None]),
            gru,
            keras.layers.Dropout(0.5),
            keras.layers.Dense(self.vocab_size)
        ])

    def compile(self):
        self.model.compile(optimizer = tf.train.AdamOptimizer(), loss = tf.losses.sparse_softmax_cross_entropy)

    def fit(self, model_dir, dataset, epochs):
        checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(str(model_dir.joinpath("ckpt_{epoch}")), save_weights_only=True, period=5, verbose=1)
        earlystop_callback = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=3, verbose=1)

        start_time = time.time()
        history = self.model.fit(dataset.repeat(), epochs=epochs, steps_per_epoch=self.batch_size, callbacks=[checkpoint_callback, earlystop_callback])
        elapsed_time = time.time() - start_time
        print("Time taken for learning {} epochs: {:.3f} minutes ({:.3f} minutes / epoch )".format(epochs, elapsed_time / 60, (elapsed_time / epochs) / 60))

        return history

    ## Train model from the dataset
    def train(self, dataset):
        optimizer = tf.train.AdamOptimizer()
        loss_f = tf.losses.sparse_softmax_cross_entropy

        for (batch, (input, target)) in enumerate(dataset):
            with tf.GradientTape() as tape:
                # feeding the hidden state back into the model
                predictions = self.model(input)

                # reshape target to make loss function expect the target
                loss = loss_f(target, predictions)

            gradients = tape.gradient(loss, self.model.variables)
            optimizer.apply_gradients(zip(gradients, self.model.variables))

            print("Batch: {}, Loss: {:.4f}".format(batch + 1, loss), end="\r")

        return loss.numpy()

    def save(self, model_dir):
        if Path.is_dir(model_dir) is not True:
            Path.mkdir(model_dir, parents=True)

        with model_dir.joinpath("parameters.json").open('w', encoding='utf-8') as params:
            params.write(json.dumps(self.parameters()))

        self.model.save_weights(str(Path(model_dir.joinpath("weights"))))

    def load(self, model_dir):
        self.model.load_weights(self.path(Path(model_dir)))

    def generate_text(self, dataset, start_string, gen_size=1, temp=1.0, delimiter=None):
        generated_text = []
        # Vectorize start_string
        try:
            input_eval = tf.expand_dims(dataset.vocab_to_indices(start_string), 0)
            print("Start string:", start_string)
        except KeyError:
            print("Unknown word included")
            return ""

        # Randomness of text generation
        temperature = temp

        count = 0
        self.model.reset_states()
        with tqdm(desc="Generating...", total=gen_size) as pbar:
            while count < gen_size:
                predictions = self.model(input_eval)
                # remove the batch dimension
                predictions = tf.squeeze(predictions, 0)

                # Using the multinomial distribution to predict the word returned by the model
                predictions = predictions / temperature
                predicted_id = tf.multinomial(predictions, num_samples=1)[-1, 0].numpy()

                # Pass the predicted word as the next input to the model along with the previous hidden state
                input_eval = tf.expand_dims([predicted_id], 0)

                char = dataset.idx2vocab[predicted_id]
                generated_text.append(char)

                if char == delimiter or not delimiter:
                    count += 1
                    pbar.update()

        return start_string + "".join(generated_text) + "\n"

    ## Return the path to <ckpt_dir>/checkpoint
    @staticmethod
    def path(ckpt_dir):
        return tf.train.latest_checkpoint(str(Path(ckpt_dir)))

    ## Return model settings as dict
    def parameters(self):
        return {
            'embedding_dim': self.embedding_dim,
            'units': self.units,
            'batch_size': self.batch_size,
            'cpu_mode': self.cpu_mode
        }
