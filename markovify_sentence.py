import argparse
import multiprocessing as mp
import sys
import time
from pathlib import Path

import markovify

from modules.combine_sentence import combine_sentence


# Generate text from the model
def generate(queue, model, count):
    while True:
        text = model.make_sentence()
        count.value += 1

        if text is not None:
            queue.put(combine_sentence(text.split()))
            break


# Wrapper method of generate()
# Because Pool.map() can give only one argument, give this method tuple value and extract it before giving extract()
def generate_sentence(args):
    generate(*args)


# Extract values in queue
def dump_queue(queue):
    ret = []
    while queue.empty() is False:
        ret.append(queue.get())

    return ret


def main():
    cores = mp.cpu_count()

    parser = argparse.ArgumentParser(description="Generate sentence with Markov chain.")
    parser.add_argument("input", type=str, help="Input file path")
    parser.add_argument("-o", "--output", type=str, help="Output file path (default: stdout)")
    parser.add_argument("-n", "--number", type=int, default=1, help="The number of sentence you want to generate (default: 1)")
    parser.add_argument("-j", "--jobs", type=int, default=int(cores / 2), help="The number of processes (default: half of the number of your CPU cores)")
    parser.add_argument("-s", "--states", type=int, default=2, help="The size of states (default: 2)")
    parser.add_argument("--encoding", type=str, default='utf-8', help="Encoding of target text file (default: utf-8)")
    args = parser.parse_args()

    with Path(args.input).open(encoding=args.encoding) as file:
        # Create markov chain model
        model = markovify.NewlineText(file.read(), state_size=args.states)

    # Prevent maximum number of processes be larger than number of sentences to generate
    jobs = min([args.jobs, args.number])
    mgr = mp.Manager()
    generated_sentences = mgr.Queue()
    # Count is incorrect if multiprocessing is enabled
    count = mgr.Value('i', 0)

    print("Processes:", jobs)
    start_time = time.time()
    with mp.Pool(jobs) as pool:
        pool.map(generate_sentence, [(generated_sentences, model, count) for _ in range(args.number)])

    elapsed_time = time.time() - start_time

    generated_sentences = "\n".join(dump_queue(generated_sentences)) + "\n"
    if args.output:
        with Path(args.output).open('w', encoding='utf-8') as out:
            out.write(generated_sentences)
    else:
        sys.stdout.write(generated_sentences)

    # Print result
    print("{} times generation to generate {} sentences (failed {:.2f}%)".format(
        count.value,
        args.number,
        ((count.value - args.number) / count.value) * 100
    ))
    print("Times taken for generation {:.3f} seconds ({:.3f} sentences / second)".format(
        elapsed_time,
        args.number / elapsed_time
    ))


if __name__ == '__main__':
    main()
