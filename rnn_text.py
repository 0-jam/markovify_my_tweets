import argparse
import time
from pathlib import Path
import tensorflow as tf
tf.enable_eager_execution()
from modules.model import Model
from modules.dataset import TextDataset
import json
from rnn_sentence import init_generator

def main():
    parser = argparse.ArgumentParser(description="Generate sentence with RNN (generation only, without model training)")
    parser.add_argument("input", type=str, help="Path to the dataset file")
    parser.add_argument("start_string", type=str, help="Path to the start string file")
    parser.add_argument("model_dir", type=str, help="Path to the learned model directory")
    parser.add_argument("-o", "--output", type=str, help="Path to save the generated text (default: None (put into stdout))")
    parser.add_argument("-g", "--gen_size", type=int, default=1, help="The number of line that you want to generate (default: 1)")
    parser.add_argument("-t", "--temperature", type=float, default=1.0, help="Set randomness of text generation (default: 1.0)")
    parser.add_argument("--encoding", type=str, default='utf-8', help="Encoding of target text file (default: utf-8)")
    args = parser.parse_args()

    ## Parse options and initialize some parameters
    gen_size = args.gen_size
    input_path = Path(args.input)
    model_dir = Path(args.model_dir)
    filename = input_path.name
    encoding = args.encoding

    with input_path.open(encoding=encoding) as file:
        text = file.read()

    with model_dir.joinpath("parameters.json").open(encoding='utf-8') as params:
        embedding_dim, units, batch_size, cpu_mode = json.load(params).values()

    ## Create the dataset from the text
    dataset = TextDataset(text, batch_size)
    generator = init_generator(dataset, model_dir)

    with Path(args.start_string).open(encoding=encoding) as input:
        if args.output:
            print("Saving generated text...")
            with Path(args.output).open('a', encoding='utf-8') as out:
                for line in input:
                    start_string = line.strip("\n")
                    out.write(generator.generate_text(dataset, start_string, gen_size=gen_size, temp=args.temperature))
        else:
            for line in input:
                start_string = line.strip("\n")
                print(generator.generate_text(dataset, start_string, gen_size, temp=args.temperature))

if __name__ == '__main__':
    main()
