import argparse
from pathlib import Path

## Divide text by word using specified engine
def divide(text, engine="janome"):
    if engine in {"janome"}:
        from modules.wakachi_janome import divide_text
    elif engine in {"mecab"}:
        from modules.wakachi_mecab import divide_text
    else:
        # If specified invalid engine, just return input text
        return text

    return divide_text(text)

def main():
    parser = argparse.ArgumentParser(description="Preprocessing script for Japanese text.")
    parser.add_argument("input", type=str, help="Input file path")
    parser.add_argument("output", type=str, help="Output file path")
    parser.add_argument("-e", "--engine", type=str, default="mecab", choices=["janome", "mecab"], help="Tokenize engine (default: mecab)")

    args = parser.parse_args()

    with Path(args.input).open() as input, Path(args.output).open('w') as out:
        out.write("\n".join(divide(input.readlines(), args.engine)) + "\n")

if __name__ == '__main__':
    main()
