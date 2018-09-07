import markovify
import argparse
import time
import multiprocessing as mp

## モデルから文章生成（処理の本体）
def generate(queue, model):
    while True:
        text = model.make_sentence()

        if text is not None:
            # 生成した文章をqueueに挿入
            queue.put(text)
            break

## ラッパーメソッド
# Pool.map()は指定できる引数の数に制限があるので、ここの引数にtuple型の値を入れて、
# このメソッド内で展開して本体メソッドで処理をする
def generate_sentence(args):
    generate(*args)

## queueの中身を抽出してlistで返す
def dump_queue(queue):
    ret = []
    while queue.empty() is False:
        ret.append(queue.get())

    return ret

def main():
    # CPUコア数取得
    cores = mp.cpu_count()

    # オプション設定・取得
    parser = argparse.ArgumentParser(description="Generate sentence with Markov chain.")
    parser.add_argument("input", type=str, help="input file path")
    parser.add_argument("-o", "--output", type=str, default="out.txt", help="output file path (default: 'out.txt')")
    parser.add_argument("-n", "--number", type=int, default=1, help="the number of sentence you want to generate (default: 1)")
    parser.add_argument("-p", "--processes", type=int, default=cores, help="the number of processes run at once (default: number of your CPU cores)")
    args = parser.parse_args()

    queue = mp.Manager().Queue()
    print("Processes:", args.processes)
    pool = mp.Pool(args.processes)

    ## ファイル読んでマルコフ連鎖モデル作成
    with open(args.input) as input:
        model = markovify.Text(input.read())

    start_time = time.time()

    pool.map(generate_sentence, [(queue, model) for _ in range(args.number)])

    # 処理にかかった時間を記録
    elapsed_time = time.time() - start_time

    with open(args.output, 'w') as out:
        out.write("\n".join(dump_queue(queue)))

    # 計測結果表示
    print("It takes {:.3f} seconds ({:.3f} sentences / second)".format(elapsed_time, args.number / elapsed_time))

if __name__ == '__main__':
    main()
