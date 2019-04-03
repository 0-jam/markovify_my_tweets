# Regenerate Sentences

- Text generation using Markov chain / Recurrent Neural Network (selectable)
- Using [markovify][markovify] to apply Markov chain
- Using [TensorFlow][tensorflow] to apply RNN

---

1. [Environment](#environment)
   1. [Software](#software)
1. [Todo](#todo)
1. [Installation](#installation)
   1. [Preprocessing scripts](#preprocessing-scripts)
   1. [Text generating scripts](#text-generating-scripts)
1. [Usage](#usage)
   1. [pp_aozora.py](#pp_aozorapy)
   1. [wakachi.py](#wakachipy)
   1. [markovify_sentence.py](#markovify_sentencepy)
   1. [rnn_sentence.py & wrnn_sentence.py & w2v_sentence.py](#rnn_sentencepy--wrnn_sentencepy--w2v_sentencepy)
   1. [bm_rnn_sentence.py](#bm_rnn_sentencepy)
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
   1. [Former Rule (Regulation #2, 20181205)](#former-rule-regulation-2-20181205)

---

## Environment

### Software

- Python 3.7.3
- Tested OSs
    - Ubuntu 18.04.2 + ROCm 2.1
    - Ubuntu 18.04.2 + CUDA 10.0 + CuDNN 7.5.0.56
- TensorFlow 1.13.1 (< 2.0)

## Todo

- [ ] Simplify specifying hyper parameters
- [ ] Separate building the dataset and the model
    - There is a lot of duplicated code around them
- [ ] Make executable from anywhere as the Web API
- [ ] Prepare for upgrading to TensorFlow 2.0
- [ ] Try [Seq2Seq](https://blog.keras.io/a-ten-minute-introduction-to-sequence-to-sequence-learning-in-keras.html)
    - The program seems to work successfully, but output does not make any sense ...
- [ ] Separate RNN trainer and generator
- [ ] Some cleanup tasks for RNN text generation
- [x] ROCm 2.x
- [x] Move benchmarking to the another repository
- [x] TensorFlow 1.13 + CUDA 10.0
    - CUDA 10.1 doesn't work because `libcublas.so` is missing
- [x] Add search options to Utanet scraper
    - Added option to set attribute to search
- [x] ~~Try word2vec~~
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
- [x] Merge [Benchmarking script](https://github.com/0-jam/regen_sentence_bm) into here
    - [x] Script
    - [x] Dataset
        - Automatically download from my Google Drive
    - [x] README
- [x] Enable saving model for RNN-based generation
- [x] Recurrent Neural Network
- [x] Multiprocessing
    - The script gets about 2.5x faster when it spawns 4 processes

## Installation

### Preprocessing scripts

- [Juman++ download page][jumanpp]
- No external modules needed for `json_extractor.py`

```bash
# Common
$ pip install tqdm

### wakachi.py
## Use Janome as the word dividing engine
$ pip install janome

## Use MeCab as the word dividing engine
$ sudo apt install mecab-ipadic-utf8 mecab libmecab-dev swig
$ pip install mecab-python3
# (Optional, only works on Linux) Install additional dictionary for Mecab
$ sudo apt install curl
$ git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git ~/mecab-ipadic-neologd
$ cd ~/mecab-ipadic-neologd
$ ./bin/install-mecab-ipadic-neologd -n -a -y

## Use Juman++ as the word dividing engine
# Install Juman++
# Download tarball from official page, extract it, and enter to the extracted directory
$ ./configure --prefix=$HOME/.local
$ make -j$(nproc)
$ make install
$ pip install pyknp
$ export PATH="$HOME/.local/bin:$PATH"

### utanet_scraper.py
$ pip install beautifulscraper
```

### Text generating scripts

```bash
## markovify_sentence.py
$ pip install markovify

## rnn_sentence.py, bm_rnn_sentence.py and wrnn_sentence.py
# If you use pyenv, install liblzma header before building Python
$ sudo apt install liblzma-dev
$ pyenv install 3.7.3
# If you have NVIDIA GPU, install tensorflow-gpu instead of tensorflow to enable CUDA-based computing
# If you have AMD GPU, install tensorflow-rocm instead of tensorflow to enable HIP + MIOpen-based computing
$ pip install tensorflow matplotlib
## w2v_sentence.py
$ pip install gensim
```

## Usage

Execute with `-h` option when you want to see the help.

### pp_aozora.py

- Preprocessing script for Aozora Bunko
- ~~Enable word dividing with `-e` option~~ Temporarily removed
    - ~~This function is also available in `run_pp_aozora.sh`~~

```bash
$ python pp_aozora.py wagahaiwa_nekodearu_{,noruby_}utf8.txt
$ python pp_aozora.py wagahaiwa_nekodearu_{,wakachi_}utf8.txt

# Execute pp_aozora.py for specific directory
$ bash run_pp_aozora.sh -i text/novel_orig/souseki -o text/novel/souseki
```

### wakachi.py

- Preprocessing script for Japanese text

```bash
$ python wakachi.py wagahaiwa_nekodearu_noruby_utf8.txt wagahaiwa_nekodearu_wakachi_utf8.txt

# Execute wakachi.py for specific directory
$ bash run_wakachi.sh -i text/novel/souseki -o text/novel_wakachi/souseki -m
```

### markovify_sentence.py

```bash
# Give filename to "-o" option if you want to save generated text
$ python markovify_sentence.py souseki_wakachi.txt -n 100
```

### rnn_sentence.py & wrnn_sentence.py & w2v_sentence.py

- Based on [this script](https://github.com/0-jam/tf_tutorials/blob/master/text_generation.py)
- It takes very long time for execution ...
    - The text worte in Japanese, precision improves a little by converting all sentences into Katakana
        - `$ mecab -O yomi`

```bash
# If you want to force to use Non-CuDNN GRU layer, give "--cpu_mode" option
# Character-based training
# No preprocessing needed for input file
$ python rnn_sentence.py souseki_utf8.txt "吾輩" -e 10

# Word-based training
# It requires text that is divided by words
$ python wrnn_sentence.py souseki_wakachi.txt "吾輩" -e 10

# Specifying learned model
# Example: Learned model exists in directory "./learned_models/Latin-Lipsum.txt"
$ ls learned_models/Latin-Lipsum.txt/
Latin-Lipsum.txt.data-00000-of-00001  Latin-Lipsum.txt.index  checkpoint
# Specify the directory name
# Training model is automatically skipped
$ python rnn_sentence.py text/Latin-Lipsum.txt "Lorem " --model_dir learned_models/Latin-Lipsum.txt
```

### bm_rnn_sentence.py

```bash
# Just execute:
$ python bm_rnn_sentence.py
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

### Former Rule (Regulation #2, 20181205)

1. Time measurement begins when training of the model is started
1. Keep training for an hour (default)
1. If it exceeded the time limit, finish training at the current epoch
    - Example: time limit is 15 minutes
        - If it elapsed 15 minutes while training epoch 3, abort training when finished training epoch 3
    - If it learned 50 epochs within the time limit, stop learning regardless of elapsed time
1. Print results
    - Elapsed time
    - Trained epochs
    - Epochs per minute
    - The value of loss function
    - Generated text
        - The number of characters: 20 lines

[markovify]: https://github.com/jsvine/markovify
[tensorflow]: https://www.tensorflow.org/
[aozora]: https://www.aozora.gr.jp/
[janome]: http://mocobeta.github.io/janome/
[jumanpp]: http://nlp.ist.i.kyoto-u.ac.jp/index.php?JUMAN++
[mecab]: http://taku910.github.io/mecab/
