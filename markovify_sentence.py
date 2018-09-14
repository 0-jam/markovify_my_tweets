import markovify
import argparse
import time
import multiprocessing as mp

## モデルから文章生成（処理の本体）
def generate(queue, model, count):
    while True:
        text = model.make_sentence()
        count.value += 1

        if text is not None:
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
    cores = mp.cpu_count()

    parser = argparse.ArgumentParser(description="Generate sentence with Markov chain.")
    parser.add_argument("input", type=str, help="input file path")
    parser.add_argument("-o", "--output", type=str, default="out.txt", help="output file path (default: 'out.txt')")
    parser.add_argument("-n", "--number", type=int, default=1, help="the number of sentence you want to generate (default: 1)")
    parser.add_argument("-j", "--jobs", type=int, default=int(cores / 2), help="the number of processes (default: half of the number of your CPU cores)")
    parser.add_argument("-s", "--states", type=int, default=2, help="the size of states (default: 2)")
    args = parser.parse_args()

    with open(args.input) as input:
        # マルコフ連鎖モデル作成
        # state_sizeは2か3がちょうどよさそう
        # 4以上になると生成失敗が多くなりはじめる
        model = markovify.NewlineText(input.read(), state_size=args.states)

    # 生成したい文数と指定されたプロセス数のうち少ないほうをプロセス数に指定（余分なプロセスができないようにするため）
    jobs = min([args.jobs, args.number])
    mgr = mp.Manager()
    generated_sentences = mgr.Queue()
    # 生成処理が実行された回数…だが、複数プロセスの場合不正確
    count = mgr.Value('i', 0)

    print("Processes:", jobs)
    start_time = time.time()
    with mp.Pool(jobs) as pool:
        pool.map(generate_sentence, [(generated_sentences, model, count) for _ in range(args.number)])

    # 処理にかかった時間を記録
    elapsed_time = time.time() - start_time

    with open(args.output, 'w') as out:
        out.write("\n".join(dump_queue(generated_sentences)) + "\n")

    # 計測結果表示
    print("{} times generation to generate {} sentences (failed {:.2f}%)".format(
        count.value,
        args.number,
        ((count.value - args.number) / count.value) * 100
    ))
    print("Times taken for generation {:.3f} seconds ({:.3f} sentences / second)".format(
        elapsed_time,
        args.number / elapsed_time)
    )

if __name__ == '__main__':
    main()
