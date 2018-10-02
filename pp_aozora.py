import argparse
import re
from pathlib import Path

## 引数sentenceを整形
def replace_sentence(sentence):
    # 不要な記号を削除
    sentence = re.sub("《.+?》|［.+?］|｜|　", "", sentence.strip())
    # 不要な記号を半角スペースに置換
    sentence = re.sub("〔|〕", " ", sentence)

    return sentence

def replace_text(text):
    text = [replace_sentence(line) for line in text]
    # 空行（もともと空行だったものと処理の結果空行になったもの）を削除して返す
    return list(filter(lambda line: line != "", text))

def main():
    # オプション設定・取得
    parser = argparse.ArgumentParser(description="Preprocessing for Aozora Bunko.")
    parser.add_argument("input", type=str, help="input file path")
    parser.add_argument("output", type=str, help="output file path")
    parser.add_argument("-e", "--engine", type=str, default="", choices=["", "janome", "mecab"], help="specify tokenize engine (default: none)")

    args = parser.parse_args()

    with Path(args.input).open() as input, Path(args.output).open('w') as out:
        text = replace_text(input.readlines())

        if args.engine != "":
            from wakachi import divide

            text = divide(text, args.engine)

        # 改行区切りでファイルに書き込む
        out.write("\n".join(text) + "\n")

if __name__ == '__main__':
    main()
