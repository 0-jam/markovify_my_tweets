import argparse
from pathlib import Path
import json
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from modules.wakachi.mecab import divide_word
import multiprocessing as mp

NUM_CPU = mp.cpu_count()
D2V_EPOCHS = 100


def main():
    parser = argparse.ArgumentParser(description="Classify sentence with doc2vec")
    # Required arguments
    parser.add_argument("input", type=str, help="Input JSON file path generated from utanet_scraper.py")
    parser.add_argument("generated_file", type=str, help="Generated lyrics from rnn_sentence.py")
    parser.add_argument("--d2vmodel", type=str, help="Doc2vec model path")
    args = parser.parse_args()

    if args.d2vmodel:
        print("Loading doc2vec model...")
        d2vmodel = Doc2Vec.load(args.d2vmodel)
    else:
        input_path = Path(args.input)
        with input_path.open(encoding='utf-8') as json_data:
            dataset = json.load(json_data).values()

        # Attribute as data or labels
        data_attr = "lyric"
        label_attrs = ["artist"]

        print("Generating doc2vec model...")
        docs = [TaggedDocument(divide_word(data[data_attr]), tags=[data[attr] for attr in label_attrs]) for data in dataset]
        d2vmodel = Doc2Vec(docs, vector_size=256, window=5, min_count=1, epochs=D2V_EPOCHS, workers=NUM_CPU)
        d2vmodel.save(input_path.stem + ".model")

    with Path(args.generated_file).open() as generated_lyrics:
        for i, generated_lyric in enumerate(generated_lyrics):
            print("Song", i)
            print(d2vmodel.docvecs.most_similar([d2vmodel.infer_vector(divide_word(generated_lyric))]))


if __name__ == "__main__":
    main()
