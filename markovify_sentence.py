import argparse
from pathlib import Path

from modules.mcmodel import MCModel


def main():
    parser = argparse.ArgumentParser(description='Generate sentence with Markov chain')
    parser.add_argument('input', type=str, help='Input file path')
    parser.add_argument('-o', '--out_path', type=str, help="Path to save the model file (default: './<input_file_name>_mc.json')")
    parser.add_argument('-m', '--mcmodel', type=str, help='Path to load the model file (default: None)')
    parser.add_argument('-s', '--states', type=int, default=2, help='The size of states (default: 2)')
    parser.add_argument('-e', '--encoding', type=str, default='utf-8', help='Encoding of target text file (default: utf-8)')
    parser.add_argument('-c', '--char_level', action='store_true', help='Change to character-based text generation')
    parser.add_argument('-g', '--gen_size', type=int, help='The number of character that you want to generate')
    args = parser.parse_args()

    model = MCModel()
    model.build_dataset(args.input, char_level=args.char_level, encoding=args.encoding)
    model.build_model(states=args.states)

    if args.out_path:
        out_path = args.out_path
    else:
        out_path = str(Path(args.input).stem) + '_mc.json'

    model.save_model(out_path)

    generated_sentence = model.generate_sentence(args.gen_size)
    print(generated_sentence)


if __name__ == '__main__':
    main()
