import argparse
import time
from pathlib import Path
import tensorflow as tf
tf.enable_eager_execution()
from modules.model import Model
from modules.dataset import TextDataset
from modules.plot_result import save_result, show_result
import settings
import json

def load_settings():
    return settings.DEFAULT_PARAMETERS

def load_test_settings():
    return settings.TEST_MODE_PARAMETERS

## Evaluation methods
# Load learned model
def init_generator(dataset, model_dir):
    with Path(model_dir).joinpath("parameters.json").open(encoding='utf-8') as params:
        parameters = json.load(params)
        embedding_dim, units, batch_size, cpu_mode = parameters.values()

    generator = Model(dataset.vocab_size, embedding_dim, units, 1, force_cpu=cpu_mode)
    generator.load(model_dir)

    return generator

def main():
    parser = argparse.ArgumentParser(description="Generate sentence with RNN")
    ## Required arguments
    parser.add_argument("input", type=str, help="Input file path")
    parser.add_argument("start_string", type=str, help="Generation start with this string")
    ## Common arguments
    parser.add_argument("-o", "--output", type=str, help="Path to save losses graph and the generated text (default: None (show without saving))")
    parser.add_argument("--encoding", type=str, default='utf-8', help="Encoding of input text file (default: utf-8)")
    parser.add_argument("--test_mode", action='store_true', help="Apply settings to run in short-time for debugging. Epochs and gen_size options are ignored (default: false)")
    ## Arguments for training
    parser.add_argument("-s", "--save_dir", type=str, help="Location to save the model checkpoint (default: './learned_models/<input_file_name>', overwrite if checkpoint already exists)")
    parser.add_argument("-c", "--cpu_mode", action='store_true', help="Force to create CPU compatible model (default: False)")
    parser.add_argument("-e", "--epochs", type=int, default=10, help="The number of epochs (default: 10)")
    parser.add_argument("--disable_point_saving", action='store_true', help="Disable to save model every 5 epochs for saving memory (default: False)")
    ## Arguments for generation
    parser.add_argument("--model_dir", type=str, help="Path to the learned model directory. Training model will be skipped.")
    parser.add_argument("-g", "--gen_size", type=int, default=1, help="The number of line that you want to generate (default: 1)")
    parser.add_argument("-t", "--temperature", type=float, default=1.0, help="Set randomness of text generation (default: 1.0)")
    args = parser.parse_args()

    ## Parse options and initialize some parameters
    if args.test_mode:
        parameters = load_test_settings()
        epochs = 3

        gen_size = 1
    else:
        parameters = load_settings()
        epochs = args.epochs

        gen_size = args.gen_size

    parameters["cpu_mode"] = args.cpu_mode
    embedding_dim, units, batch_size, cpu_mode = parameters.values()
    input_path = Path(args.input)
    filename = input_path.name
    encoding = args.encoding

    with input_path.open(encoding=encoding) as file:
        text = file.read()

    ## Create the dataset from the text
    dataset = TextDataset(text, batch_size)

    ## Create the model
    model = Model(dataset.vocab_size, embedding_dim, units, dataset.batch_size, force_cpu=cpu_mode)

    # Specify directory to save model
    if args.save_dir:
        model_dir = Path(args.save_dir)
    elif args.model_dir:
        model_dir = Path(args.model_dir)
    else:
        model_dir = Path("./learned_models").joinpath(filename)

    if not args.model_dir:
        losses = []
        start = time.time()
        for epoch in range(epochs):
            # Actual epoch number (for displaying)
            epoch_num = epoch + 1

            print("Epoch: {} / {}:".format(epoch_num, epochs))
            epoch_start = time.time()

            loss = model.train(dataset.dataset)
            losses.append(loss)

            print("Time taken for epoch {} / {}: {:.3f} sec, Loss: {:.3f}".format(
                epoch_num,
                epochs,
                time.time() - epoch_start,
                loss
            ))

            if (epoch_num) % 5 == 0 and not args.disable_point_saving:
                print("Saving current model...")
                model.save(model_dir, parameters)

            # If ARC (Average Rate of Change) of last 5 epochs is under 0.1%, stop learning
            last_losses = losses[-5:]
            try:
                arc = (last_losses[4] - last_losses[0]) / (len(last_losses) - 1)
                print("ARC of last {} epochs: {}".format(len(last_losses), arc))
                if abs(arc) < 0.003:
                    epochs = epoch
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

        # Save models and hyper parameters
        model.save(model_dir, parameters)

    generator = init_generator(dataset, model_dir)
    generated_text = generator.generate_text(dataset, args.start_string, gen_size=gen_size, temp=args.temperature)

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
