# Regenerate Sentences

- Text generation using Markov chain / Recurrent Neural Network (selectable)
- Using [markovify][markovify] to apply Markov chain
- Using [TensorFlow][tensorflow] to apply RNN

---

1. [Environment](#environment)
    1. [Software](#software)
1. [Installation (Common)](#installation-common)
    1. [pip modules](#pip-modules)
1. [Installation (Ubuntu 18.04)](#installation-ubuntu-1804)
    1. [Word dividing engine](#word-dividing-engine)
        1. [MeCab](#mecab)
        1. [(UNUSED) Juman++](#unused-juman)
    1. [Text generating scripts](#text-generating-scripts)
        1. [rnn_sentence.py](#rnn_sentencepy)
        1. [classify_lyric.py](#classify_lyricpy)
1. [Installation (Arch Linux)](#installation-arch-linux)
    1. [Word dividing engine](#word-dividing-engine-1)
    1. [Text generating scripts](#text-generating-scripts-1)
1. [Usage](#usage)
    1. [pp_aozora.py](#pp_aozorapy)
    1. [markovify_sentence.py](#markovify_sentencepy)
    1. [rnn_sentence.py](#rnn_sentencepy-1)
    1. [utanet_scraper.py](#utanet_scraperpy)
    1. [json_extractor.py](#json_extractorpy)
    1. [cat_json.py](#cat_jsonpy)
    1. [classify_lyric.py](#classify_lyricpy-1)
1. [Preprocessing (markovify_sentence.py)](#preprocessing-markovify_sentencepy)
    1. [Aozora Bunko](#aozora-bunko)
        1. [Remove manually](#remove-manually)
        1. [Remove using pp_aozora.py](#remove-using-pp_aozorapy)
        1. [Replace with whitespace](#replace-with-whitespace)
1. [Benchmarking](#benchmarking)

---

## Environment

### Software

- Python 3.7.4
- Tested OSs
    - Ubuntu 18.04.2 (Linux 4.18.0) + ROCm 2.6
    - Ubuntu 18.04.2 (Linux 4.18.0 + NVIDIA 410.48) + CUDA 10.0 + CuDNN 7.5.0.56
    - Arch Linux (Linux 5.3.7 + NVIDIA 435.21) + CUDA 10.1.243 + CuDNN 7.6.4.38
- TensorFlow 2.0.0
    - ... with a lot of deprecation warnings

## Installation (Common)

### pip modules

```
$ pipenv install
```

## Installation (Ubuntu 18.04)

### Word dividing engine

#### MeCab

```
$ sudo apt install mecab-ipadic-utf8 mecab libmecab-dev swig
```

To install additional dictionary for Mecab

```
$ sudo apt install curl
$ git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git ~/mecab-ipadic-neologd
$ cd ~/mecab-ipadic-neologd
$ ./bin/install-mecab-ipadic-neologd -n -a -y
```

#### (UNUSED) Juman++

Download tarball from [the official page](http://nlp.ist.i.kyoto-u.ac.jp/index.php?JUMAN++), extract it, and enter to the extracted directory

```
$ ./configure --prefix=$HOME/.local
$ make -j$(nproc)
$ make install
$ pip install pyknp
$ export PATH="$HOME/.local/bin:$PATH"
```

### Text generating scripts

#### rnn_sentence.py

```bash
# If you use pyenv, install liblzma header before building Python
$ sudo apt install liblzma-dev
$ pyenv install 3.7.4
# If you have NVIDIA GPU, install tensorflow-gpu instead of tensorflow to enable CUDA-based computing
# If you have AMD GPU, install tensorflow-rocm instead of tensorflow to enable HIP + MIOpen-based computing
$ pip install tensorflow matplotlib
```

#### classify_lyric.py

```
$ pip install gensim
```

## Installation (Arch Linux)

- yay as an AUR helper

### Word dividing engine

```bash
## Use MeCab as the word dividing engine
$ yay -S mecab mecab-ipadic-neologd-git
$ pip install --user mecab-python3
# (Optional) Install additional dictionary for Mecab
# Same way as Ubuntu is also OK
$ yay -S mecab-ipadic-neologd-git
```

### Text generating scripts

```bash
## rnn_sentence.py
# If you have NVIDIA GPU, install python-tensorflow-cuda instead of python-tensorflow to enable CUDA-based computing
$ yay -S python-tensorflow-cuda
$ pip install --user matplotlib
## classify_lyric.py
$ pip install --user gensim
```

## Usage

Execute with `-h` option when you want to see the help.

### pp_aozora.py

- Preprocessing script for Aozora Bunko

```bash
$ python pp_aozora.py wagahaiwa_nekodearu_{,noruby_}utf8.txt

# Execute pp_aozora.py for specific directory
$ bash run_pp_aozora.sh -i text/novel_orig/souseki -o text/novel/souseki
```

### markovify_sentence.py

```bash
# Give filename to "-o" option if you want to save generated text
# Add -c option to character-based training
$ python markovify_sentence.py souseki_wakachi.txt
```

### rnn_sentence.py

- Based on [this script](https://github.com/0-jam/tf_tutorials/blob/master/text_generation.py)
- Recommends to execute on GPU-enabled environment

```bash
# If you don't specify start_string, generator will use a random charactor/word in the text
# Add -w option to word-based training
$ python rnn_sentence.py souseki.txt --start_string "吾輩" -e 10

# Specifying learned model
# Example: Learned model exists in directory "./learned_models/Latin-Lipsum.txt"
$ ls learned_models/Latin-Lipsum/
Latin-Lipsum.data-00000-of-00001  Latin-Lipsum.index  checkpoint
# Specify the directory name
# Training model is automatically skipped
$ python rnn_sentence.py text/Latin-Lipsum.txt --load_dir learned_models/Latin-Lipsum
```

### utanet_scraper.py

- Do scraping and extract song informations from [Utanet（歌ネット）](https://www.uta-net.com/)
- Song information is saved as JSON
    - key: song_id from original URL
    - values:
        - title
        - artist
        - lyricist
        - composer
        - lyric
- Available attributes to search
    - 'title'
    - 'artist'
    - 'lyricist'
    - 'composer'

```bash
# Extracted song information is saved as "songs.json" by default (It can be specified with -o option)
$ python utanet_scraper.py "秋元康"
$ python utanet_scraper.py "AKB48" -a 'artist'
```

### json_extractor.py

- Extract specified attributes from [utanet_scraper.py](#utanet_scraperpy)
    - Specifing multiple attributes are **not** available
- Extracted attributes are saved as plain text
    - Each songs are delimited by line break
- Available attributes
    - 'id'
    - 'title'
    - 'artist'
    - 'lyricist'
    - 'composer'
    - 'lyric'

```bash
# Default attribute: lyrics
$ python json_extractor.py akimoto.json akimoto_lyrics.txt
```

### cat_json.py

- Combine multiple JSON files in the specified directory

```bash
# Input as the directory, output as the file name
$ python cat_json.py text/lyrics_json lyrics_all.json
```

### classify_lyric.py

- Classify generated lyrics by artist or lyricist
- Using [doc2vec](https://radimrehurek.com/gensim/models/doc2vec.html)

```bash
# Specify --d2vmodel option to use pretrained doc2vec model
$ python classify_lyric.py text/lyrics_all.json generated_texts/aki_kosoado_512.txt
```

## Preprocessing (markovify_sentence.py)

- Make sure each words is separated by whitespaces before executing
- In Windows, you will get `UnicodeDecodeError: 'cp932' codec can't decode byte 0x99 in position xxxx` unless input file encoding is not Shift-JIS
- You will get `KeyError: ('\_\_\_BEGIN\_\_', '\_\_\_BEGIN\_\_')` if there is hankaku symbols in the input file

### Aozora Bunko

- Convert all zenkaku alphabets & numbers, brackets `（）`, zenkaku space, `！`, `？` to hankaku
    - `unicodedata.normalize('NFKC', text)`

#### Remove manually

- Title
- Author
- Convert text encoding into UTF-8 by using such as `$ nkf -w` (Text encoding of downloaded file is Shift-JIS)

#### Remove using pp_aozora.py

```python
# Apply on entire text
regex1 = "---.*---\n|底本：.*"
# Apply on every line in text
regex2 = "　|^\n+|《.+?》|［.+?］|｜"
```

- _【テキスト中に現れる記号について】_ (About symbols in the text)
- Footnote（_底本：_）
- Removed by using `strip()`
    - Zenkaku whitespace
        - > 　吾輩は猫である。名前はまだ無い。
    - Sequential blank line
- Furigana and ｜ (Zenkaku vertical bar) indicates the beginning of the string which is placed furigana
    - > しかもあとで聞くとそれは書生という人間中で一番 **｜** 獰悪 **《どうあく》** な種族であったそうだ。
- Annotation
    - > **［＃８字下げ］** 一 **［＃「一」は中見出し］**

#### Replace with whitespace

```
〔|〕
```

- Start of the sentence written in Latin character
    - > 〔Quid aliud est mulier nisi amicitiae& inimica〕

## Benchmarking

- Moved to [0-jam/regen_sentence_bm](https://github.com/0-jam/regen_sentence_bm)
- Records of benchmarking is [here](https://gist.github.com/0-jam/f21f44375cb70b987e99cda485d6940d)

[markovify]: https://github.com/jsvine/markovify
[tensorflow]: https://www.tensorflow.org/
[aozora]: https://www.aozora.gr.jp/
[janome]: http://mocobeta.github.io/janome/
[jumanpp]: http://nlp.ist.i.kyoto-u.ac.jp/index.php?JUMAN++
[mecab]: http://taku910.github.io/mecab/
