import argparse
import re
from pathlib import Path
import unicodedata
from modules.multi_sub import replace_str

## 引数sentenceを整形
def replace_sentence(sentence):
    # 不要な記号を削除
    sentence = re.sub("《.+?》|［.+?］|｜|　", "", sentence.strip())
    # 不要な記号を半角スペースに置換
    sentence = re.sub("〔|〕", " ", sentence)
    # unicode正規化
    sentence = unicodedata.normalize('NFKC', sentence)

    # 3つ以上続くピリオド..., 全角ピリオド・・・を三点リーダー…に置換
    # （上記normalize()で三点リーダーがピリオド3つに置換されているのをここで戻している）
    # 2回以上続く三点リーダー……を1つ…にする
    patterns = [(r"\.{3,}", "…"), (r"・{3,}", "…"), (r"…{2,}", "…")]
    sentence = replace_str(sentence, patterns)

    return sentence

def replace_text(text):
    text = re.sub(".*---\n|底本：.*", "", text, flags=(re.MULTILINE|re.DOTALL))
    text = [replace_sentence(line) for line in text.split("\n")]
    # 空行（もともと空行だったものと処理の結果空行になったもの）を削除して返す
    return list(filter(lambda line: line != "", text))

def main():
    # オプション設定・取得
    parser = argparse.ArgumentParser(description="Preprocessing for Aozora Bunko.")
    parser.add_argument("input", type=str, help="Input file path")
    parser.add_argument("output", type=str, help="Output file path")
    parser.add_argument("-e", "--engine", type=str, default="", choices=["", "janome", "mecab", "juman"], help="Tokenize engine (default: none)")

    args = parser.parse_args()

    with Path(args.input).open(encoding='utf-8') as input:
        text = replace_text(input.read())

    with Path(args.output).open('w', encoding='utf-8') as out:
        # 改行区切りでファイルに書き込む
        out.write("\n".join(text) + "\n")

if __name__ == '__main__':
    main()
