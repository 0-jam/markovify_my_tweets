import argparse
import re
from pathlib import Path

from modules.normalize_text import normalize


# 引数sentenceを整形
def replace_sentence(sentence):
    # 不要な記号を削除
    sentence = re.sub('《.+?》|［.+?］|｜|　', '', sentence.strip())
    # 不要な記号を半角スペースに置換
    sentence = re.sub('〔|〕', ' ', sentence)

    return normalize(sentence)


def replace_text(text):
    text = re.sub('.*---\n|底本：.*', '', text, flags=(re.MULTILINE | re.DOTALL))
    text = [replace_sentence(line) for line in text.splitlines()]
    # 空行（もともと空行だったものと処理の結果空行になったもの）を削除して返す
    return list(filter(lambda line: line != '', text))


def main():
    parser = argparse.ArgumentParser(description='Preprocessing for Aozora Bunko.')
    parser.add_argument('input', type=str, help='Input file path')
    parser.add_argument('output', type=str, help='Output file path')
    parser.add_argument('-e', '--engine', type=str, default='', choices=['', 'janome', 'mecab', 'juman'], help='Tokenize engine (default: none)')

    args = parser.parse_args()

    with Path(args.input).open(encoding='cp932') as input:
        text = replace_text(input.read())

    with Path(args.output).open('w', encoding='utf-8') as out:
        out.write('\n'.join(text) + '\n')


if __name__ == '__main__':
    main()
