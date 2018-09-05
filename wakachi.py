from janome.tokenizer import Tokenizer
import argparse

parser = argparse.ArgumentParser(description="<WIP> Preprocessing script for Japanese text.")
parser.add_argument("input", type=str, help="input file path")
parser.add_argument("output", type=str, help="output file path")

args = parser.parse_args()

# 分かち書き用トークナイザ
t = Tokenizer(wakati=True)

arr = []

# 読み込んだ文章を分かち書き
with open(args.input) as str:
    arr.append(t.tokenize(str.read()))

# 半角スペース区切りでファイルに書き込む
with open(args.output, 'w') as out:
    for str in arr:
        out.write(" ".join(str))
