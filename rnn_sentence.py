import argparse
import time
from pathlib import Path
import tensorflow as tf
tf.enable_eager_execution()
from modules.model import Model
from modules.dataset import TextDataset
from modules.plot_result import save_result

## Return the path to <ckpt_dir>/checkpoint
def model_path(ckpt_dir):
    return tf.train.latest_checkpoint(str(Path(ckpt_dir)))

def main():
    parser = argparse.ArgumentParser(description="Generate sentence with RNN")
    parser.add_argument("input", type=str, help="Input file path")
    parser.add_argument("start_string", type=str, help="Generation start with this string")
    parser.add_argument("-o", "--output", type=str, help="Output file path (default: stdout)")
    parser.add_argument("-e", "--epochs", type=int, default=10, help="The number of epochs (default: 10)")
    parser.add_argument("-g", "--gen_size", type=int, default=1000, help="The size of text that you want to generate (default: 1000)")
    parser.add_argument("-m", "--model_dir", type=str, help="Path to the learned model directory (default: empty (create a new model))")
    parser.add_argument("-s", "--save_dir", type=str, help="Location to save the model checkpoint (default: './learned_models/<input_file_name>', overwrite if checkpoint already exists)")
    parser.add_argument("-c", "--cpu_mode", action='store_true', help="Force to use CPU (default: False)")
    parser.add_argument("--encoding", type=str, default='utf-8', help="Encoding of target text file (default: utf-8)")
    parser.add_argument("--test_mode", action='store_true', help="Apply settings to run in short-time for debugging. Epochs and gen_size options are ignored (default: false)")
    args = parser.parse_args()

    ## Parse options and initialize some parameters
    if args.test_mode:
        # input_path = Path("text/Latin-Lipsum.txt")
        # encoding = 'utf-8'

        embedding_dim = 4
        units = 16
        epochs = 2

        # start_string = "Lorem "
        gen_size = 100
    else:
        # The embedding dimensions
        embedding_dim = 256
        # RNN (Recursive Neural Network) nodes
        units = 1024
        epochs = args.epochs

        gen_size = args.gen_size

    input_path = Path(args.input)
    encoding = args.encoding

    with input_path.open(encoding=encoding) as file:
        text = file.read()

    ## Create the dataset from the text
    dataset = TextDataset(text)

    ## Create the model
    model = Model(dataset.vocab_size, embedding_dim, units, force_cpu=args.cpu_mode)

    if args.model_dir:
        # Load learned model
        model.load_weights(model_path(args.model_dir))
    else:
        filename = input_path.name
        # Specify directory to save model
        if args.save_dir:
            path = Path(args.save_dir)
        else:
            path = Path("./learned_models").joinpath(filename)

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

        elapsed_time = time.time() - start
        print("Time taken for learning {} epochs: {:.3f} sec ({:.3f} seconds / epoch), Loss: {:.3f}\n".format(
            epochs,
            elapsed_time,
            elapsed_time / epochs,
            loss
        ))

        save_result(losses)

        if Path.is_dir(path) is not True:
            Path.mkdir(path, parents=True)

        model.save_weights(str(path.joinpath(filename).resolve()))

    ## Evaluation
    start_string = args.start_string
    generated_text = model.generate_text(dataset, start_string, gen_size)
    if args.output:
        with Path(args.output).open('w') as out:
            out.write(generated_text)
    else:
        print(generated_text)

if __name__ == '__main__':
    main()
