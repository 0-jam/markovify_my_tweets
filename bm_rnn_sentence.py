import argparse
import time
from pathlib import Path
import tensorflow as tf
tf.enable_eager_execution()
import lzma
from modules.model import Model
from modules.dataset import TextDataset
from modules.plot_result import show_result, save_result

def main():
    parser = argparse.ArgumentParser(description="Benchmarking of sentence generation with RNN.")
    parser.add_argument("-c", "--cpu_mode", action='store_true', help="Force to use CPU (default: False)")
    parser.add_argument("-t", "--test_mode", action='store_true', help="Apply settings to train model in short-time for debugging (default: false)")
    args = parser.parse_args()

    ## Create the dataset from the XZ-compressed text
    path = tf.keras.utils.get_file("souseki.txt.xz", "https://drive.google.com/uc?export=download&id=1RnvBPi0GSg07-FhiuHpkwZahGwl4sMb5")
    with lzma.open(path) as file:
        text = file.read().decode()

    dataset = TextDataset(text, 64)

    if args.test_mode:
        # The embedding dimensions
        embedding_dim = 4
        # RNN (Recursive Neural Network) nodes
        units = 16

        # Time limit (min)
        time_limit = 5

        gen_size = 1
    else:
        # The embedding dimensions
        embedding_dim = 256
        # RNN (Recursive Neural Network) nodes
        units = 1024

        # Time limit (min)
        time_limit = 60

        gen_size = 20

    ## Create the model
    model = Model(dataset.vocab_size, embedding_dim, units, dataset.batch_size, force_cpu=args.cpu_mode)

    epoch = 0
    elapsed_time = 0
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

        last_losses = losses[-3:]
        try:
            arc = (last_losses[2] - last_losses[0]) / 2
            print("ARC of last 3 epochs:", arc)
        except IndexError:
            pass

    print("Time!")
    elapsed_time = elapsed_time / 60

    print("Saving trained model...")
    today = time.strftime("%Y%m%d")
    path = Path("benchmark_" + today)
    model_dir = path.joinpath("model")
    if Path.is_dir(path) is not True:
        Path.mkdir(model_dir, parents=True)

    model.model.save_weights(str(model_dir.joinpath("model").resolve()))

    # Generate sentence from the model
    generator = Model(dataset.vocab_size, embedding_dim, units, 1, force_cpu=args.cpu_mode)
    # Load learned model
    generator.model.load_weights(model.path(model_dir))
    generated_text = generator.generate_text(dataset, "吾輩は", gen_size)

    # Show results
    print("Learned {} epochs in {:.3f} minutes ({:.3f} epochs / minute)".format(epoch, elapsed_time, epoch / elapsed_time))
    print("Loss:", loss)
    print("Saving generated text...")
    with open(str(path) + "/generated_text.txt", 'w', encoding='utf-8') as out:
        out.write(generated_text)

    save_result(losses, save_to=str(path) + "/losses_" + today + ".png")

if __name__ == '__main__':
    main()
