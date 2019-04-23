import argparse
import json
from pathlib import Path

from rnn_sentence import init_generator


def main():
    parser = argparse.ArgumentParser(description='Character-based sentence generation using RNN (generation only, without model training)')
    parser.add_argument('input', type=str, help='Path to the text file')
    parser.add_argument('start_string', type=str, help='Path to the start string file')
    parser.add_argument('model_dir', type=str, help='Path to the learned model directory')
    parser.add_argument('-o', '--output', type=str, help='Path to save the generated text (default: None (put into stdout))')
    parser.add_argument('-g', '--gen_size', type=int, default=1, help='The number of line that you want to generate (default: 1)')
    parser.add_argument('-t', '--temperature', type=float, default=1.0, help='Set randomness of text generation (default: 1.0)')
    parser.add_argument('-d', '--delimiter', type=str, default='\n', help='Set delimiter of text generation (default: newline)')
    parser.add_argument('--encoding', type=str, default='utf-8', help='Encoding of target text file (default: utf-8)')
    args = parser.parse_args()

    # Parse options and initialize some parameters
    gen_size = args.gen_size
    input_path = Path(args.input)
    model_dir = Path(args.model_dir)
    encoding = args.encoding

    with input_path.open(encoding=encoding) as file:
        text = file.read()

    with model_dir.joinpath('parameters.json').open(encoding='utf-8') as params:
        embedding_dim, units, batch_size, cpu_mode = json.load(params).values()

    generator = init_generator(model_dir, text)
    with Path(args.start_string).open(encoding=encoding) as input:
        for line in input:
            generated_text = ''.join(generator.generate_text(line.strip('\n'), gen_size=gen_size, temp=args.temperature, delimiter='\n'))
            if args.output:
                with Path(args.output).open('a', encoding='utf-8') as out:
                    out.write(generated_text)
            else:
                print(generated_text)


if __name__ == '__main__':
    main()
