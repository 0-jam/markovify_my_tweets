from janome.tokenizer import Tokenizer
import argparse

parser = argparse.ArgumentParser(description="<WIP> Preprocessing script for Japanese text.")
parser.add_argument("input", type=str, help="input file path")
parser.add_argument("output", type=str, help="output file path")

args = parser.parse_args()

# 分かち書き用トークナイザ
t = Tokenizer(wakati=True)

## 読み込んだ文章を分かち書き
def word_divide(text):
    arr = []

    for token in t.tokenize(text):
        arr.append(str(token))

    # 半角スペースを除去して返す
    return filter(lambda str:str != " ", arr)

with open(args.input) as input:
    text = word_divide(input.read())

# 半角スペース区切りでファイルに書き込む
# 行の頭にもスペースが入ってしまう
with open(args.output, 'w') as out:
    out.write(" ".join(text))
