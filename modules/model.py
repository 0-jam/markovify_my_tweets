import tensorflow as tf
from tensorflow import keras
from tqdm import tqdm
from pathlib import Path
import json

## Keras Functional API implementation
class Model():
    def __init__(self, vocab_size, embedding_dim, units, batch_size, force_cpu=False):
        # Hyper parameters
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.units = units
        self.batch_size = batch_size

        # Enable CUDA if GPU is available
        if tf.test.is_gpu_available() and not force_cpu:
            gru = keras.layers.CuDNNGRU(
                self.units,
                return_sequences=True,
                stateful=True,
                recurrent_initializer='glorot_uniform'
            )
        else:
            gru = keras.layers.GRU(
                self.units,
                return_sequences=True,
                stateful=True,
                recurrent_activation='sigmoid',
                recurrent_initializer='glorot_uniform'
            )

        self.model = keras.Sequential([
            keras.layers.Embedding(vocab_size, embedding_dim, batch_input_shape=[batch_size, None]),
            gru,
            keras.layers.Dropout(0.5),
            keras.layers.Dense(vocab_size)
        ])

        # self.model.compile(optimizer = tf.train.AdamOptimizer(), loss = tf.losses.sparse_softmax_cross_entropy)

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

    def save(self, model_dir, parameters):
        if Path.is_dir(model_dir) is not True:
            Path.mkdir(model_dir, parents=True)

        with model_dir.joinpath("parameters.json").open('w', encoding='utf-8') as params:
            params.write(json.dumps(parameters))

        self.model.save_weights(str(Path(model_dir.joinpath("weights")).resolve()))

    def load(self, model_dir):
        self.model.load_weights(self.path(Path(model_dir)))

    def generate_text(self, dataset, start_string, gen_size=1, temp=1.0, delimiter="\n"):
        generated_text = []
        # Vectorize start_string
        input_eval = tf.expand_dims(dataset.str_to_indices(start_string), 0)
        temperature = temp

        with tqdm(total=gen_size, desc="Generating...") as pbar:
            count = 0
            self.model.reset_states()
            while count < gen_size:
                predictions = self.model(input_eval)
                # remove the batch dimension
                predictions = tf.squeeze(predictions, 0)

                # Using the multinomial distribution to predict the word returned by the model
                predictions = predictions / temperature
                predicted_id = tf.multinomial(predictions, num_samples=1)[-1, 0].numpy()

                # Pass the predicted word as the next input to the model along with the previous hidden state
                input_eval = tf.expand_dims([predicted_id], 0)

                char = dataset.idx2char[predicted_id]
                generated_text.append(char)

                if char == delimiter:
                    count += 1
                    pbar.update(1)

        return start_string + "".join(generated_text) + "\n"

    ## Return the path to <ckpt_dir>/checkpoint
    @staticmethod
    def path(ckpt_dir):
        return tf.train.latest_checkpoint(str(Path(ckpt_dir)))
