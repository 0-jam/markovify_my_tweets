import argparse
from pathlib import Path
from modules.model import WordModel
from modules.plot_result import save_result, show_result
import json
from rnn_sentence import load_settings, load_test_settings

## Evaluation methods
# Load learned model
def init_generator(model_dir, text):
    embedding_dim, units, _, cpu_mode = load_settings(model_dir.joinpath("parameters.json")).values()

    generator = WordModel(embedding_dim, units, 1, text, cpu_mode=cpu_mode)
    generator.load(model_dir)

    return generator

def main():
    parser = argparse.ArgumentParser(description="Generate sentence with RNN (word-based)")
    ## Required arguments
    parser.add_argument("input", type=str, help="Input file path")
    parser.add_argument("start_string", type=str, help="Generation start with this string")
    ## Common arguments
    parser.add_argument("-o", "--output", type=str, help="Path to save losses graph and the generated text (default: None (show without saving))")
    parser.add_argument("--encoding", type=str, default='utf-8', help="Encoding of input text file (default: utf-8)")
    parser.add_argument("--test_mode", action='store_true', help="Apply settings to run in short-time for debugging. Epochs and gen_size options are ignored (default: false)")
    ## Arguments for training
    parser.add_argument("-s", "--save_dir", type=str, help="Location to save the model checkpoint (default: './learned_models/<input_file_name>', overwrite if checkpoint already exists)")
    parser.add_argument("-c", "--config", type=str, default='settings/default.json', help="Path to configuration file (default: './settings/default.json')")
    parser.add_argument("--cpu_mode", action='store_true', help="Force to create CPU compatible model (default: False)")
    parser.add_argument("-e", "--epochs", type=int, default=10, help="The number of epochs (default: 10)")
    ## Arguments for generation
    parser.add_argument("--model_dir", type=str, help="Path to the learned model directory. Training model will be skipped.")
    parser.add_argument("-g", "--gen_size", type=int, default=100, help="The number of word that you want to generate (default: 100)")
    parser.add_argument("-t", "--temperature", type=float, default=1.0, help="Set randomness of text generation (default: 1.0)")
    args = parser.parse_args()

    ## Parse options and initialize some parameters
    if args.test_mode:
        parameters = load_test_settings()
        epochs = 3

        gen_size = 10
    else:
        parameters = load_settings(args.config)
        epochs = args.epochs

        gen_size = args.gen_size

    parameters["cpu_mode"] = args.cpu_mode
    embedding_dim, units, batch_size, cpu_mode = parameters.values()
    input_path = Path(args.input)
    filename = input_path.stem
    encoding = args.encoding

    with input_path.open(encoding=encoding) as file:
        text = file.read()

    # Specify directory to save model
    if args.save_dir:
        model_dir = Path(args.save_dir)
    elif args.model_dir:
        model_dir = Path(args.model_dir)
    else:
        model_dir = Path("./learned_models").joinpath(filename + "_wrnn")

    ## Training
    if not args.model_dir:
        # Create the model
        model = WordModel(embedding_dim, units, batch_size, text, cpu_mode=cpu_mode)

        model.compile()
        history = model.fit(model_dir, epochs)
        losses = history.history["loss"]
        model.save(model_dir)

    generator = init_generator(model_dir, text)
    generated_text = " ".join(generator.generate_text(args.start_string, gen_size=gen_size, temp=args.temperature))

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
