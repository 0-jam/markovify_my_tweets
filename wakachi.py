import argparse

def main():
    parser = argparse.ArgumentParser(description="<WIP> Preprocessing script for Japanese text.")
    parser.add_argument("input", type=str, help="input file path")
    parser.add_argument("output", type=str, help="output file path")
    parser.add_argument("-e", "--engine", type=str, default="janome", choices=["janome", "mecab"], help="specify tokenize engine (default: janome)")

    args = parser.parse_args()

    engine = args.engine
    if engine in {"janome"}:
        from wakachi_janome import divide_text
    elif engine in {"mecab"}:
        from wakachi_mecab import divide_text

    with open(args.input) as input:
        text = divide_text(input.readlines())

    # 改行区切りでファイルに書き込む
    with open(args.output, 'w') as out:
        out.write("\n".join(text) + "\n")

if __name__ == '__main__':
    main()
