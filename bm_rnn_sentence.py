import argparse
import time
from pathlib import Path
import tensorflow as tf
tf.enable_eager_execution()
import lzma
from modules.model import Model
from modules.dataset import TextDataset

def main():
    parser = argparse.ArgumentParser(description="Benchmarking of sentence generation with RNN.")
    parser.add_argument("-c", "--cpu_mode", action='store_true', help="Force to use CPU (default: False)")
    args = parser.parse_args()

    # テキスト読み込み
    path = tf.keras.utils.get_file("souseki.txt.xz", "https://drive.google.com/uc?export=download&id=1RnvBPi0GSg07-FhiuHpkwZahGwl4sMb5")
    with lzma.open(path) as file:
        text = file.read().decode()

    # テキストからデータセット作成
    dataset = TextDataset(text)

    ## モデル作成
    # The embedding dimensions
    embedding_dim = 256
    # RNN (Recursive Neural Network) nodes
    units = 1024

    model = Model(dataset.vocab_size, embedding_dim, units, force_cpu=args.cpu_mode)

    epoch = 0
    elapsed_time = 0
    # 制限時間
    minutes = 60
    start = time.time()
    # この時間を経過したら…ではなく、時間切れになった時のepochの学習を終えたら学習終了
    while elapsed_time < (60 * minutes):
        epoch += 1
        print("Epoch:", epoch)
        epoch_start = time.time()

        loss = model.train(dataset.dataset)

        elapsed_time = time.time() - start
        print("Time taken for epoch {}: {:.3f} sec, Loss: {:.3f}\n".format(
            epoch,
            time.time() - epoch_start,
            loss
        ))

    print("Time!")
    elapsed_time = elapsed_time / 60

    # モデルから文章生成
    generated_text = model.generate_text(dataset, "吾輩は", 1000)
    print("Generated text:")
    print(generated_text)

    print("Learned {} epochs in {:.3f} minutes ({:.3f} epochs / minute)".format(epoch, elapsed_time, epoch / elapsed_time))
    print("Loss:", loss)

if __name__ == '__main__':
    main()