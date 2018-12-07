import argparse
from pathlib import Path
from tqdm import tqdm

## Divide text by word using specified engine
def main():
    parser = argparse.ArgumentParser(description="Preprocessing script for Japanese text.")
    parser.add_argument("input", type=str, help="Input file path")
    parser.add_argument("output", type=str, help="Output file path")
    parser.add_argument("-e", "--engine", type=str, default="mecab", choices=["janome", "mecab", "juman"], help="Tokenize engine (default: mecab)")
    parser.add_argument("-r", "--allow_empty", action='store_true', help="Don't remove empty line")

    args = parser.parse_args()

    # Select engine for word dividing
    if args.engine in {"janome"}:
        from modules.wakachi.janome import divide_word
    elif args.engine in {"mecab"}:
        from modules.wakachi.mecab import divide_word
    elif args.engine in {"juman"}:
        from modules.wakachi.juman import divide_word

    with Path(args.input).open() as input:
        text = input.readlines()

    with Path(args.output).open('a') as out:
        for line in tqdm(text):
            line = line.strip()

            if not line and not args.allow_empty:
                continue

            out.write(divide_word(line) + "\n")

if __name__ == '__main__':
    main()
