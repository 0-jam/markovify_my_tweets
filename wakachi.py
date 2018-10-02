import argparse
from pathlib import Path

## 入力されたtextをengineで分かち書き
def divide(text, engine="janome"):
    if engine in {"janome"}:
        from wakachi_janome import divide_text
    elif engine in {"mecab"}:
        from wakachi_mecab import divide_text
    else:
        # 無効なエンジンが指定された場合，入力されたテキストをそのまま返す（暫定）
        return text

    return divide_text(text)

def main():
    parser = argparse.ArgumentParser(description="Preprocessing script for Japanese text.")
    parser.add_argument("input", type=str, help="input file path")
    parser.add_argument("output", type=str, help="output file path")
    parser.add_argument("-e", "--engine", type=str, default="janome", choices=["janome", "mecab"], help="specify tokenize engine (default: janome)")

    args = parser.parse_args()

    with Path(args.input).open() as input, Path(args.output).open('w') as out:
        out.write("\n".join(divide(input.readlines(), args.engine)) + "\n")

if __name__ == '__main__':
    main()
