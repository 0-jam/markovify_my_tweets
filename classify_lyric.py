import argparse
import json
import multiprocessing as mp
import re
import unicodedata
from pathlib import Path

from gensim.models.doc2vec import Doc2Vec, TaggedDocument

from modules.transform_text import deconjugate_sentence, remove_stopwords

NUM_CPU = mp.cpu_count()
D2V_EPOCHS = 100


# 引数sentenceを整形
def replace_sentence(sentence):
    # unicode正規化
    sentence = unicodedata.normalize('NFKC', sentence)
    # 不要な記号を削除
    sentence = re.sub(r'\W', '', sentence.strip())

    return sentence


# Preprocess the text for Doc2Vec
def preprocess_text(text):
    normalized_text = replace_sentence(text)
    divided_text = deconjugate_sentence(normalized_text)

    return remove_stopwords(divided_text)


def main():
    parser = argparse.ArgumentParser(description='Classify sentence with doc2vec')
    # Required arguments
    parser.add_argument('input', type=str, help='Input JSON file path generated from utanet_scraper.py')
    parser.add_argument('generated_file', type=str, help='Generated lyrics from rnn_sentence.py')
    parser.add_argument('--d2vmodel', type=str, help='Doc2vec model path')
    args = parser.parse_args()

    if args.d2vmodel:
        print('Loading doc2vec model...')
        d2vmodel = Doc2Vec.load(args.d2vmodel)
    else:
        input_path = Path(args.input)
        with input_path.open(encoding='utf-8') as json_data:
            dataset = json.load(json_data).values()

        # Attribute as data or labels
        data_attr = 'lyric'
        label_attrs = ['artist']

        print('Generating doc2vec model...')
        docs = [TaggedDocument(preprocess_text(data[data_attr]), tags=[unicodedata.normalize('NFKC', data[attr]) for attr in label_attrs]) for data in dataset]
        d2vmodel = Doc2Vec(docs, vector_size=256, window=5, min_count=3, epochs=D2V_EPOCHS, workers=NUM_CPU)
        d2vmodel.save(input_path.stem + '.model')

    with Path(args.generated_file).open() as generated_lyrics:
        for i, generated_lyric in enumerate(generated_lyrics):
            print('Song', i)
            print(d2vmodel.docvecs.most_similar([d2vmodel.infer_vector(preprocess_text(generated_lyric))]))


if __name__ == '__main__':
    main()
