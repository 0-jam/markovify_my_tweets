import argparse
import time
from pathlib import Path
import tensorflow as tf
tf.enable_eager_execution()
from modules.model import Model
from modules.dataset import TextDataset
import json

def main():
    parser = argparse.ArgumentParser(description="Generate sentence with RNN (generation only, without model training)")
    parser.add_argument("input", type=str, help="Input file path")
    parser.add_argument("start_string", type=str, help="Generation start with this string")
    parser.add_argument("model_dir", type=str, help="Path to the learned model directory")
    parser.add_argument("-o", "--output", type=str, help="Path to save the generated text (default: None (put into stdout))")
    parser.add_argument("-g", "--gen_size", type=int, default=1, help="The number of line that you want to generate (default: 1)")
    parser.add_argument("-t", "--temperature", type=float, default=1.0, help="Set randomness of text generation (default: 1.0)")
    parser.add_argument("--encoding", type=str, default='utf-8', help="Encoding of target text file (default: utf-8)")
    args = parser.parse_args()

    ## Parse options and initialize some parameters
    gen_size = args.gen_size

    input_path = Path(args.input)
    filename = input_path.name
    encoding = args.encoding

    with input_path.open(encoding=encoding) as file:
        text = file.read()

    with Path(args.model_dir).joinpath("parameters.json").open(encoding='utf-8') as params:
        embedding_dim, units, batch_size, cpu_mode = json.load(params).values()

    ## Create the dataset from the text
    dataset = TextDataset(text, batch_size)

    ## Evaluation
    generator = Model(dataset.vocab_size, embedding_dim, units, 1, force_cpu=cpu_mode)
    # Load weights from learned model
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
