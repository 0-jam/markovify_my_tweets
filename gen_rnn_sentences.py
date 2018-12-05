import argparse
import time
from pathlib import Path
import tensorflow as tf
tf.enable_eager_execution()
from modules.model import Model
from modules.dataset import TextDataset

def main():
    parser = argparse.ArgumentParser(description="Generate sentence with RNN")
    parser.add_argument("input", type=str, help="Input file path")
    parser.add_argument("start_string", type=str, help="Generation start with this string")
    parser.add_argument("model_dir", type=str, help="Path to the learned model directory")
    parser.add_argument("-o", "--output", type=str, help="Path to save the generated text (default: None (put into stdout))")
    parser.add_argument("-g", "--gen_size", type=int, default=1, help="The number of line that you want to generate (default: 1)")
    parser.add_argument("-t", "--temperature", type=float, default=1.0, help="Set randomness of text generation (default: 1.0)")
    parser.add_argument("-c", "--cpu_mode", action='store_true', help="Force to load CPU compatible model (default: False)")
    parser.add_argument("--encoding", type=str, default='utf-8', help="Encoding of target text file (default: utf-8)")
    parser.add_argument("--test_mode", action='store_true', help="Apply settings to run in short-time for debugging. Epochs and gen_size options are ignored (default: false)")
    args = parser.parse_args()

    ## Parse options and initialize some parameters
    if args.test_mode:
        embedding_dim = 4
        units = 16
        batch_size = 128

        gen_size = 1
    else:
        # The embedding dimensions
        embedding_dim = 256
        # RNN (Recursive Neural Network) nodes
        units = 2048
        batch_size = 64

        gen_size = args.gen_size

    input_path = Path(args.input)
    filename = input_path.name
    encoding = args.encoding

    with input_path.open(encoding=encoding) as file:
        text = file.read()

    ## Create the dataset from the text
    dataset = TextDataset(text, batch_size)

    ## Evaluation
    generator = Model(dataset.vocab_size, embedding_dim, units, 1, force_cpu=args.cpu_mode)
    # Load learned model
    generator.load(args.model_dir)

    start_string = args.start_string
    generated_text = generator.generate_text(dataset, start_string, gen_size, args.temperature)
    if args.output:
        print("Saving generated text...")
        with Path(args.output).open('w', encoding='utf-8') as out:
            out.write(generated_text)
    else:
        print(generated_text)

if __name__ == '__main__':
    main()
