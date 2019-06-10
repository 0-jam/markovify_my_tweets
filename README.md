# Regenerate Sentences

- Text generation using Markov chain / Recurrent Neural Network (selectable)
- Using [markovify][markovify] to apply Markov chain
- Using [TensorFlow][tensorflow] to apply RNN

---

1. [Environment](#environment)
   1. [Software](#software)
1. [Todo](#todo)
1. [Installation (Ubuntu 18.04)](#installation-ubuntu-1804)
   1. [Preprocessing scripts](#preprocessing-scripts)
   1. [Word dividing engine](#word-dividing-engine)
   1. [Text generating scripts](#text-generating-scripts)
1. [Installation (Arch Linux)](#installation-arch-linux)
   1. [Preprocessing scripts](#preprocessing-scripts-1)
   1. [Word dividing engine](#word-dividing-engine-1)
   1. [Text generating scripts](#text-generating-scripts-1)
1. [Usage](#usage)
   1. [pp_aozora.py](#pp_aozorapy)
   1. [markovify_sentence.py](#markovify_sentencepy)
   1. [rnn_sentence.py](#rnn_sentencepy)
   1. [utanet_scraper.py](#utanet_scraperpy)
   1. [json_extractor.py](#json_extractorpy)
   1. [cat_json.py](#cat_jsonpy)
   1. [classify_lyric.py](#classify_lyricpy)
1. [Preprocessing (markovify_sentence.py)](#preprocessing-markovify_sentencepy)
   1. [Aozora Bunko](#aozora-bunko)
      1. [Remove manually](#remove-manually)
      1. [Remove using pp_aozora.py](#remove-using-pp_aozorapy)
      1. [Replace with whitespace](#replace-with-whitespace)
1. [Benchmarking](#benchmarking)

---

## Environment

### Software

- Python 3.7.3
- Tested OSs
    - Ubuntu 18.04.2 (Linux 4.18.0) + ROCm 2.1
    - Ubuntu 18.04.2 (Linux 4.18.0 + NVIDIA 410.48) + CUDA 10.0 + CuDNN 7.5.0.56
    - Arch Linux (Linux 5.1.4 + NVIDIA 430.14) + CUDA 10.1.168 + CuDNN 7.5.1.10
- TensorFlow 1.13.1 (< 2.0)

## Todo

- [ ] Try [SeqGAN](https://github.com/LantaoYu/SeqGAN)
- [ ] Generic Doc2vec classifier
- [ ] Remove unneeded words (i.e. stopwords) on Uta-net classifier
- [ ] Simplify specifying hyper parameters
- [ ] Prepare for upgrading to TensorFlow 2.0
- [ ] ROCm 2.x + Arch Linux
- [x] Saving/loading tokenizer to enable text generation without specifying original text
- [x] Separate RNN trainer and generator
    - Added generation-only script
- [x] Separate building the dataset and the model
- [x] Some cleanup tasks for RNN text generation
    - Unified RNN text generator between character-based and word-based
- [x] Move benchmarking to the another repository
- [x] TensorFlow 1.13 + CUDA 10.0
    - CUDA 10.1 doesn't work because `libcublas.so` is missing
    - There is CUDA 10.1 convertible build in [Arch Linux repo](https://www.archlinux.org/packages/community/x86_64/tensorflow-cuda/) and it works
- [x] Add search options to Utanet scraper
    - Added option to set attribute to search
- [x] Enable function to use word as a token for RNN-based generation
- [x] Enable using various engine for word dividing
    - [x] [Juman++][jumanpp]
        - Juman++ cannot build on WSL
    - [x] [MeCab][mecab]
- [x] Text formatter for [Aozora bunko][aozora]
    - [x] Remove title, author and footnotes
    - [x] Remove annotation symbols
- [x] Windows port
    - [x] Text encoding
    - [x] Create directory to save learned model
- [x] Enable saving model for RNN-based generation
- [x] Recurrent Neural Network
- [x] Multiprocessing
    - The script gets about 2.5x faster when it spawns 4 processes

## Installation (Ubuntu 18.04)

### Preprocessing scripts

- No external modules needed for `json_extractor.py`

```bash
# Common
$ pip install tqdm

### utanet_scraper.py
$ pip install beautifulscraper
```

### Word dividing engine

- [Juman++ download page][jumanpp]

```bash
## Use MeCab as the word dividing engine
$ sudo apt install mecab-ipadic-utf8 mecab libmecab-dev swig
$ pip install mecab-python3
# (Optional) Install additional dictionary for Mecab
$ sudo apt install curl
$ git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git ~/mecab-ipadic-neologd
$ cd ~/mecab-ipadic-neologd
$ ./bin/install-mecab-ipadic-neologd -n -a -y

## (UNUSED) Use Juman++ as the word dividing engine
# Install Juman++
# Download tarball from official page, extract it, and enter to the extracted directory
$ ./configure --prefix=$HOME/.local
$ make -j$(nproc)
$ make install
$ pip install pyknp
$ export PATH="$HOME/.local/bin:$PATH"
```

### Text generating scripts

```bash
## markovify_sentence.py
$ pip install markovify

## rnn_sentence.py
# If you use pyenv, install liblzma header before building Python
$ sudo apt install liblzma-dev
$ pyenv install 3.7.3
# If you have NVIDIA GPU, install tensorflow-gpu instead of tensorflow to enable CUDA-based computing
# If you have AMD GPU, install tensorflow-rocm instead of tensorflow to enable HIP + MIOpen-based computing
$ pip install tensorflow matplotlib
## classify_lyric.py
$ pip install gensim
```

## Installation (Arch Linux)

- yay as an AUR helper

### Preprocessing scripts

```bash
# If you doesn't install pip, install it at first
$ yay -S python-pip

# Common
$ pip install --user tqdm

### utanet_scraper.py
$ pip install --user beautifulscraper
```

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
## markovify_sentence.py
$ pip install --user markovify

## rnn_sentence.py
# If you have NVIDIA GPU, install python-tensorflow-cuda instead of python-tensorflow to enable CUDA-based computing
# TensorFlow in pip package and the original source code is not compatible with CUDA 10.1 (2019/5/27)
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
$ python markovify_sentence.py souseki.txt
```

### rnn_sentence.py

- Based on [this script](https://github.com/0-jam/tf_tutorials/blob/master/text_generation.py)
- It takes very long time for execution ...
    - The text worte in Japanese, precision improves a little by converting all sentences into Katakana
        - `$ mecab -O yomi`

```bash
# If you want to force to use Non-CuDNN GRU layer, give "--cpu_mode" option
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
