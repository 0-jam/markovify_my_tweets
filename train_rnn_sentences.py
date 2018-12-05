import argparse
import time
from pathlib import Path
import tensorflow as tf
tf.enable_eager_execution()
from modules.model import Model
from modules.dataset import TextDataset
from modules.plot_result import save_result, show_result

def main():
    parser = argparse.ArgumentParser(description="Train RNN model generating sentence")
    parser.add_argument("input", type=str, help="Input file path")
    parser.add_argument("-o", "--output", type=str, help="Output file path (default: stdout)")
    parser.add_argument("-e", "--epochs", type=int, default=10, help="The number of epochs (default: 10)")
    parser.add_argument("-s", "--save_dir", type=str, help="Location to save the model checkpoint (default: './learned_models/<input_file_name>', overwrite if checkpoint already exists)")
    parser.add_argument("-c", "--cpu_mode", action='store_true', help="Force to create CPU compatible model (default: False)")
    parser.add_argument("--encoding", type=str, default='utf-8', help="Encoding of target text file (default: utf-8)")
    parser.add_argument("--test_mode", action='store_true', help="Apply settings to run in short-time for debugging. Epochs and gen_size options are ignored (default: false)")
    args = parser.parse_args()

    ## Parse options and initialize some parameters
    if args.test_mode:
        embedding_dim = 4
        units = 16
        epochs = 3
        batch_size = 128
    else:
        # The embedding dimensions
        embedding_dim = 256
        # RNN (Recursive Neural Network) nodes
        units = 2048
        epochs = args.epochs
        batch_size = 64

    input_path = Path(args.input)
    filename = input_path.name
    encoding = args.encoding

    with input_path.open(encoding=encoding) as file:
        text = file.read()

    ## Create the dataset from the text
    dataset = TextDataset(text, batch_size)

    ## Create the model
    model = Model(dataset.vocab_size, embedding_dim, units, dataset.batch_size, force_cpu=args.cpu_mode)

    # Specify directory to save model
    if args.save_dir:
        path = Path(args.save_dir)
    else:
        path = Path("./learned_models").joinpath(input_path.name)

    losses = []
    start = time.time()
    for epoch in range(epochs):
        print("Epoch: {} / {}:".format(epoch + 1, epochs))
        epoch_start = time.time()

        loss = model.train(dataset.dataset)
        losses.append(loss)

        print("Time taken for epoch {} / {}: {:.3f} sec, Loss: {:.3f}\n".format(
            epoch + 1,
            epochs,
            time.time() - epoch_start,
            loss
        ))

        # If ARC (Average Rate of Change) of last 3 epochs is under 0.1%, stop learning
        last_losses = losses[-3:]
        try:
            arc = (last_losses[2] - last_losses[0]) / (len(last_losses) - 1)
            print("ARC of last {} epochs: {}".format(len(last_losses), arc))
            if abs(arc) < 0.01:
                print("Stopped learning")
                epochs = epoch
                break
        except IndexError:
            pass

    elapsed_time = time.time() - start
    print("Time taken for learning {} epochs: {:.3f} sec ({:.3f} seconds / epoch), Loss: {:.3f}\n".format(
        epochs,
        elapsed_time,
        elapsed_time / epochs,
        loss
    ))

    print("Saving trained model...")
    if Path.is_dir(path) is not True:
        Path.mkdir(path, parents=True)

    model.model.save_weights(str(path.joinpath(filename).resolve()))

    if args.output:
        print("Saving losses graph...")
        save_result(losses)
    else:
        show_result(losses)

if __name__ == '__main__':
    main()
