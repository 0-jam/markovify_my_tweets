import argparse
from pathlib import Path

from modules.plot_result import save_result
from modules.text_model import TextModel
from modules.combine_sentence import combine_sentence


def main():
    parser = argparse.ArgumentParser(description='Generate sentence with RNN')
    # Required arguments
    parser.add_argument('input', type=str, help='Input file path')
    # Common arguments
    parser.add_argument('-o', '--output', type=str, help='Path to save losses graph and the generated text (default: None (show without saving))')
    parser.add_argument('--encoding', type=str, default='utf-8', help='Encoding of input text file (default: utf-8)')
    parser.add_argument('--test_mode', action='store_true', help="Apply settings to run in short-time for debugging. Option '--config', '--epochs' and '--gen_size' options are ignored (default: false)")
    parser.add_argument('-w', '--word_based', action='store_true', help='Change to word-based RNN (default: False)')
    # Arguments for training
    parser.add_argument('-s', '--save_dir', type=str, help="Location to save the model checkpoint (default: './learned_models/<input_file_name>', overwrite if checkpoint already exists)")
    parser.add_argument('-c', '--config', type=str, default='settings/default.json', help="Path to configuration file (default: './settings/default.json')")
    parser.add_argument('-e', '--epochs', type=int, default=10, help='The number of epochs (default: 10)')
    # Arguments for generation
    parser.add_argument('--start_string', type=str, help='Generation start with this string (default: None (generate from the random string in the input text))')
    parser.add_argument('-g', '--gen_size', type=int, default=1000, help='The number of character that you want to generate (default: 1000)')
    parser.add_argument('-t', '--temperature', type=float, default=1.0, help='Set randomness of text generation (default: 1.0)')
    args = parser.parse_args()

    input_path = Path(args.input)

    # Specify directory to save model
    if args.save_dir:
        save_dir = Path(args.save_dir)
    else:
        save_dir = Path('./learned_models').joinpath(input_path.stem)

    # Parse options and initialize some parameters
    if args.test_mode:
        params_json = 'settings/test.json'
        epochs = 3

        gen_size = 100
    else:
        params_json = args.config
        epochs = args.epochs

        gen_size = args.gen_size

    # Initialize the model
    model = TextModel()
    model.set_parameters_from_json(params_json)

    # Training
    model.build_dataset(str(input_path), encoding=args.encoding, char_level=not args.word_based)
    # Create the model
    model.build_trainer()

    model.compile()
    history = model.fit(save_dir, epochs)
    losses = history.history['loss']
    model.save_trainer(save_dir)

    model.build_generator(save_dir)
    model.save_generator(save_dir)

    generated_text = model.generate_text(args.start_string, gen_size=gen_size, temperature=args.temperature)

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

    print('Saving losses graph ...')
    save_result(losses, str(save_dir.joinpath('losses.png')))


if __name__ == '__main__':
    main()
