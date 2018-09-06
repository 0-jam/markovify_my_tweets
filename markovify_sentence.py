import markovify
import argparse
import time

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
    # 生成処理をした回数
    count = 0
    start_time = time.time()

    for _ in range(args.number):
        while True:
            count += 1
            # 作ったモデルから文章生成
            text = model.make_sentence()

            if text is not None:
                # ファイルに書き込む
                out.write(text + "\n")
                break

    # 処理にかかった時間を記録
    elapsed_time = time.time() - start_time

    # 計測結果表示
    print("{} times generation to generate {} sentences (failed {:.2f}%)".format(
        count,
        args.number,
        ((count - args.number) / count) * 100
    ))
    print("It takes {:.3f} seconds".format(elapsed_time))
