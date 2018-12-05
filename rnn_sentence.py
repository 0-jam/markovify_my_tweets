import argparse
import time
from pathlib import Path
import tensorflow as tf
tf.enable_eager_execution()
from modules.model import Model
from modules.dataset import TextDataset
from modules.plot_result import save_result, show_result
import settings

def load_settings():
    return settings.DEFAULT_PARAMETERS.values()

def load_test_settings():
    return settings.TEST_MODE_PARAMETERS.values()

def main():
    parser = argparse.ArgumentParser(description="Generate sentence with RNN")
    parser.add_argument("input", type=str, help="Input file path")
    parser.add_argument("start_string", type=str, help="Generation start with this string")
    parser.add_argument("-o", "--output", type=str, help="Path to save losses graph and the generated text (default: None (show without saving))")
    parser.add_argument("-e", "--epochs", type=int, default=10, help="The number of epochs (default: 10)")
    parser.add_argument("-g", "--gen_size", type=int, default=1, help="The number of line that you want to generate (default: 1)")
    parser.add_argument("-t", "--temperature", type=float, default=1.0, help="Set randomness of text generation (default: 1.0)")
    parser.add_argument("-m", "--model_dir", type=str, help="Path to the learned model directory (default: empty (create a new model))")
    parser.add_argument("-s", "--save_dir", type=str, help="Location to save the model checkpoint (default: './learned_models/<input_file_name>', overwrite if checkpoint already exists)")
    parser.add_argument("-c", "--cpu_mode", action='store_true', help="Force to create CPU compatible model (default: False)")
    parser.add_argument("--encoding", type=str, default='utf-8', help="Encoding of target text file (default: utf-8)")
    parser.add_argument("--test_mode", action='store_true', help="Apply settings to run in short-time for debugging. Epochs and gen_size options are ignored (default: false)")
    args = parser.parse_args()

    ## Parse options and initialize some parameters
    if args.test_mode:
        embedding_dim, units, batch_size = load_test_settings()
        epochs = 3

        gen_size = 1
    else:
        # The embedding dimensions
        embedding_dim, units, batch_size = load_settings()
        epochs = args.epochs

        gen_size = args.gen_size

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
    elif args.model_dir:
        # Load learned model
        path = Path(args.model_dir)
    else:
        path = Path("./learned_models").joinpath(input_path.name)

    if not args.model_dir:
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
                    break
            except IndexError:
                pass

        elapsed_time = time.time() - start
        print("Training finished.")
        print("Time taken for learning {} epochs: {:.3f} sec ({:.3f} seconds / epoch), Loss: {:.3f}\n".format(
            epochs,
            elapsed_time,
            elapsed_time / epochs,
            loss
        ))

        if Path.is_dir(path) is not True:
            Path.mkdir(path, parents=True)

        model.save(path.joinpath(filename))

    ## Evaluation
    generator = Model(dataset.vocab_size, embedding_dim, units, 1, force_cpu=args.cpu_mode)
    # Load learned model
    generator.load(path)

    start_string = args.start_string
    generated_text = generator.generate_text(dataset, start_string, gen_size, args.temperature)
    if args.output:
        print("Saving generated text...")
        outpath = Path(args.output)
        with outpath.open('w', encoding='utf-8') as out:
            out.write(generated_text)

        try:
            save_result(losses, outpath)
        except NameError:
            print("Skipped drawing losses graph")
    else:
        print(generated_text)

        try:
            show_result(losses)
        except NameError:
            print("Skipped drawing losses graph")

if __name__ == '__main__':
    main()
