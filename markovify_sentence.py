import markovify
import argparse

parser = argparse.ArgumentParser(description="Generate sentence with Markov chain.")
parser.add_argument("input", type=str, help="input file path")
parser.add_argument("-o", "--output", type=str, default="out.txt", help="output file path (default: 'out.txt')")
parser.add_argument("-n", "--number", type=int, default=1, help="the number of sentence you want to generate (default: 1)")

args = parser.parse_args()

## ファイル読んでマルコフ連鎖モデル作成
def marcovify_text(file):
    with open(file) as str:
        text = str.read()

    return markovify.Text(text)

model = marcovify_text(args.input)

with open(args.output, 'w') as out:
    arr = []
    for i in range(args.number):
        # 作ったモデルから文章生成
        arr.append(model.make_sentence())

    # カラ(NoneType)の要素を削除
    arr = list(filter(None, arr))
    # ファイルに書き込む
    out.write("\n".join(arr))

    # 指定した文（行）数に対して何文（行）生成されたか表示
    print("Generated {} / Specified {} ({:.2f}%)".format(len(arr), args.number, (len(arr) / args.number * 100)))
