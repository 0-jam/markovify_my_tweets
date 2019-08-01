import argparse
from pathlib import Path

from modules.text_model import TextModel
from modules.combine_sentence import combine_sentence


def main():
    parser = argparse.ArgumentParser(description='Generate sentence with RNN without training the model')
    # Required arguments
    parser.add_argument('load_dir', type=str, help='Path to the learned model directory')
    # Common arguments
    parser.add_argument('-o', '--output', type=str, help='Path to save the generated text (default: None (show without saving))')
    # Arguments for generation
    parser.add_argument('--start_string', type=str, help='Generation start with this string (default: None (generate from the random string in the input text))')
    parser.add_argument('-g', '--gen_size', type=int, default=1000, help='The number of character that you want to generate (default: 1000)')
    parser.add_argument('-t', '--temperature', type=float, default=1.0, help='Set randomness of text generation (default: 1.0)')
    args = parser.parse_args()

    # Specify directory to load the model
    model_dir = Path(args.load_dir)
    model = TextModel()

    # Generate-only
    model.load_generator(model_dir)

    generated_text = model.generate_text(args.start_string, gen_size=args.gen_size, temperature=args.temperature)

    if model.is_word_based():
        generated_text = combine_sentence(generated_text)
    else:
        generated_text = ''.join(generated_text)

    if args.output:
        print('Saving generated text...')
        outpath = Path(args.output)
        with outpath.open('w', encoding='utf-8') as out:
            out.write(generated_text + '\n')
    else:
        print(generated_text)


if __name__ == '__main__':
    main()
