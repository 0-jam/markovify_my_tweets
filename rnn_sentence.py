import argparse
import numpy as np
import time
from pathlib import Path
import tensorflow as tf
tf.enable_eager_execution()
from tqdm import tqdm
from modules.model import Model

## Return the path to <ckpt_dir>/checkpoint
def model_path(ckpt_dir):
    return tf.train.latest_checkpoint(str(Path(ckpt_dir)))

## Create input and target texts from the text
def split_into_target(chunk):
    input_text = chunk[:-1]
    target_text = chunk[1:]

    return input_text, target_text

## Using sparse_softmax_cross_entropy so that we don't have to create one-hot vectors
def loss_function(real, preds):
    return tf.losses.sparse_softmax_cross_entropy(labels=real, logits=preds)

def main():
    parser = argparse.ArgumentParser(description="Generate sentence with RNN. README.md contains further information.")
    parser.add_argument("input", type=str, help="input file path")
    parser.add_argument("start_string", type=str, help="generation start with this string")
    parser.add_argument("-o", "--output", type=str, help="output file path (default: stdout)")
    parser.add_argument("-e", "--epochs", type=int, default=10, help="the number of epochs (default: 10)")
    parser.add_argument("-g", "--gen_size", type=int, default=1000, help="the size of text that you want to generate (default: 1000)")
    parser.add_argument("-m", "--model_dir", type=str, help="path to the learned model directory (default: empty (create a new model))")
    parser.add_argument("-s", "--save_to", type=str, help="location to save the model checkpoint (default: './learned_models/<input_file_name>', overwrite if checkpoint already exists)")
    parser.add_argument("-c", "--cpu_mode", action='store_true', help="Force to use CPU (default: False)")
    args = parser.parse_args()

    with Path(args.input).open() as file:
        text = file.read()

    ## Vectorize the text
    text_size = len(text)
    # unique character in text
    vocab = sorted(set(text))
    vocab_size = len(vocab)
    print("Text has {} characters ({} unique characters)".format(text_size, vocab_size))
    # Creating a mapping from unique characters to indices
    # This list doesn't have character that is not contained in the text
    char2idx = {char:index for index, char in enumerate(vocab)}
    idx2char = np.array(vocab)
    text_as_int = np.array([char2idx[c] for c in text])

    # The maximum length sentence we want for single input in characters
    seq_length = 100
    chunks = tf.data.Dataset.from_tensor_slices(text_as_int).batch(seq_length + 1, drop_remainder=True)

    batch_size = 64
    # Buffer size to shuffle the dataset
    buffer_size = 10000

    ## Creating batches and shuffling them
    dataset = chunks.map(split_into_target)
    dataset = dataset.shuffle(buffer_size).batch(batch_size, drop_remainder=True)

    ## Create the model
    embedding_dim = 256
    # embedding_dim = 16
    # RNN (Recursive Neural Network) nodes
    units = 1024
    # units = 64

    model = Model(vocab_size, embedding_dim, units, force_cpu=args.cpu_mode)
    optimizer = tf.train.AdamOptimizer()

    if args.model_dir:
        # Load learned model
        model.load_weights(model_path(args.model_dir))
    else:
        filename = args.input.split("/")[-1]
        epochs = args.epochs
        # Specify directory to save model
        if args.save_to:
            path = Path(args.save_to)
        else:
            path = Path("./learned_models").joinpath(filename)

        start = time.time()
        for epoch in range(epochs):
            print("Epoch: {} / {}:".format(epoch + 1, epochs))
            epoch_start = time.time()

            # initializing the hidden state at the start of every epoch
            hidden = model.reset_states()

            for (batch, (input, target)) in enumerate(dataset):
                with tf.GradientTape() as tape:
                    # feeding the hidden state back into the model
                    predictions, hidden = model(input, hidden)

                    # reshape target to make loss function expect the target
                    target = tf.reshape(target, (-1,))
                    loss = loss_function(target, predictions)

                gradients = tape.gradient(loss, model.variables)
                optimizer.apply_gradients(zip(gradients, model.variables))

                print("Batch: {}, Loss: {:.4f}".format(batch + 1, loss), end="\r")

            print("Time taken for epoch {} / {}: {:.3f} sec, Loss: {:.3f}\n".format(
                epoch + 1,
                epochs,
                time.time() - epoch_start,
                loss.numpy()
            ))

        elapsed_time = time.time() - start
        print("Time taken for learning {} epochs: {:.3f} sec ({:.3f} seconds / epoch), Loss: {:.3f}\n".format(
            epochs,
            elapsed_time,
            elapsed_time / epochs,
            loss.numpy()
        ))

        if Path.is_dir(path) is not True:
            Path.mkdir(path, parents=True)

        model.save_weights(str(path.joinpath(filename)))

    ## Evaluation
    gen_size = args.gen_size
    generated_text = ''
    start_string = args.start_string
    # Vectorize start_string
    input_eval = tf.expand_dims([char2idx[s] for s in start_string], 0)
    temperature = 1.0

    # hidden layer shape: (batch_size, units)
    hidden = [tf.zeros((1, units))]

    for i in tqdm(range(gen_size), desc="Generating..."):
        predictions, hidden = model(input_eval, hidden)

        # Using the multinomial distribution to predict the word returned by the model
        predictions = predictions / temperature
        predicted_id = tf.multinomial(predictions, num_samples=1)[-1, 0].numpy()

        # Pass the predicted word as the next input to the model along with the previous hidden state
        input_eval = tf.expand_dims([predicted_id], 0)

        generated_text += idx2char[predicted_id]

    generated_text = start_string + generated_text + "\n"
    if args.output:
        with Path(args.output).open('w') as out:
            out.write(generated_text)
    else:
        print(generated_text)

if __name__ == '__main__':
    main()
