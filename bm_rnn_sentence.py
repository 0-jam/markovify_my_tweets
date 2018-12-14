import argparse
import time
from pathlib import Path
import tensorflow as tf
tf.enable_eager_execution()
import lzma
from modules.model import Model
from modules.dataset import TextDataset
from modules.plot_result import show_result, save_result
from rnn_sentence import load_settings, load_test_settings, init_generator

def main():
    parser = argparse.ArgumentParser(description="Benchmarking of sentence generation with RNN.")
    parser.add_argument("-e", "--max_epochs", type=int, default=50, help="Max number of epochs (default: 50)")
    parser.add_argument("-c", "--cpu_mode", action='store_true', help="Force to use CPU (default: False)")
    parser.add_argument("-t", "--test_mode", action='store_true', help="Apply settings to train model in short-time for debugging, ignore -e option (default: false)")
    args = parser.parse_args()

    ## Create the dataset from the XZ-compressed text
    path = tf.keras.utils.get_file("souseki.txt.xz", "https://drive.google.com/uc?export=download&id=1RnvBPi0GSg07-FhiuHpkwZahGwl4sMb5")
    with lzma.open(path) as file:
        text = file.read().decode()

    if args.test_mode:
        parameters = load_test_settings()

        # Time limit (min)
        time_limit = 5
        max_epochs = 2

        gen_size = 1
    else:
        parameters = load_settings()

        # Time limit (min)
        time_limit = 60
        max_epochs = args.max_epochs

        gen_size = 20

    parameters["cpu_mode"] = args.cpu_mode
    embedding_dim, units, batch_size, cpu_mode = parameters.values()

    ## Create the dataset & the model
    dataset = TextDataset(text, batch_size)
    model = Model(dataset.vocab_size, embedding_dim, units, dataset.batch_size, force_cpu=cpu_mode)

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
        print("Time taken for epoch {}: {:.3f} sec, Loss: {:.3f}".format(
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

        if epoch >= max_epochs:
            print("You have learned enough epochs! Aborting...")
            break

    print("Time!")
    elapsed_time = elapsed_time / 60

    print("Saving trained model...")
    today = time.strftime("%Y%m%d")
    result_dir = Path("benchmark_" + today)
    model_dir = result_dir.joinpath("model")

    model.save(model_dir, parameters)

    # Generate sentence from the model
    generator = init_generator(dataset, model_dir)
    generated_text = generator.generate_text(dataset, "吾輩は", gen_size)

    # Show results
    print("Learned {} epochs in {:.3f} minutes ({:.3f} epochs / minute)".format(epoch, elapsed_time, epoch / elapsed_time))
    print("Loss:", loss)
    print("Saving generated text...")
    with open(str(result_dir) + "/generated_text.txt", 'w', encoding='utf-8') as out:
        out.write(generated_text)

    save_result(losses, save_to=str(result_dir) + "/losses_" + today + ".png")

if __name__ == '__main__':
    main()
