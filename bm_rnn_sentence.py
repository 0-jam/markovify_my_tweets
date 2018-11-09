import argparse
import time
from pathlib import Path
import tensorflow as tf
tf.enable_eager_execution()
import lzma
from modules.model import Model
from modules.dataset import TextDataset
from modules.plot_result import show_result

def main():
    parser = argparse.ArgumentParser(description="Benchmarking of sentence generation with RNN.")
    parser.add_argument("-c", "--cpu_mode", action='store_true', help="Force to use CPU (default: False)")
    args = parser.parse_args()

    ## Create the dataset from the XZ-compressed text
    path = tf.keras.utils.get_file("souseki.txt.xz", "https://drive.google.com/uc?export=download&id=1RnvBPi0GSg07-FhiuHpkwZahGwl4sMb5")
    with lzma.open(path) as file:
        text = file.read().decode()

    dataset = TextDataset(text)

    ## Create the model
    # The embedding dimensions
    embedding_dim = 256
    # RNN (Recursive Neural Network) nodes
    units = 1024

    model = Model(dataset.vocab_size, embedding_dim, units, force_cpu=args.cpu_mode)

    epoch = 0
    elapsed_time = 0
    # Time limit (min)
    time_limit = 60
    losses = []
    start = time.time()
    # Finish training in current epoch when time limit exceeded
    while elapsed_time < (60 * time_limit):
        epoch += 1
        print("Epoch:", epoch)
        epoch_start = time.time()

        loss = model.train(dataset.dataset)
        losses.append(loss)

        elapsed_time = time.time() - start
        print("Time taken for epoch {}: {:.3f} sec, Loss: {:.3f}\n".format(
            epoch,
            time.time() - epoch_start,
            loss
        ))

    print("Time!")
    elapsed_time = elapsed_time / 60

    # Generate sentence from the model
    generated_text = model.generate_text(dataset, "吾輩は", 1000)
    print("Generated text:")
    print(generated_text)

    print("Learned {} epochs in {:.3f} minutes ({:.3f} epochs / minute)".format(epoch, elapsed_time, epoch / elapsed_time))
    print("Loss:", loss)
    show_result(losses)

if __name__ == '__main__':
    main()
