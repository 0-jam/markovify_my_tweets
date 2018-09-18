import argparse

## 入力されたtextをengineで分かち書き
def divide(engine, text):
    if engine in {"janome"}:
        from wakachi_janome import divide_text
    elif engine in {"mecab"}:
        from wakachi_mecab import divide_text
    else
        # 無効なエンジンが指定された場合，入力されたテキストをそのまま返す（暫定）
        return text

    return divide_text(text)

def main():
    parser = argparse.ArgumentParser(description="<WIP> Preprocessing script for Japanese text.")
    parser.add_argument("input", type=str, help="input file path")
    parser.add_argument("output", type=str, help="output file path")
    parser.add_argument("-e", "--engine", type=str, default="janome", choices=["janome", "mecab"], help="specify tokenize engine (default: janome)")

    args = parser.parse_args()

    with open(args.input) as input, open(args.output, 'w') as out:
        out.write("\n".join(divide(args.engine, input.readlines())) + "\n")

if __name__ == '__main__':
    main()
