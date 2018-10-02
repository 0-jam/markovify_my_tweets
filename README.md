# Regenerate Sentences

- Text generation using Markov chain / Recurrent Neural Network (selectable)
- Using [markovify][markovify] to apply Markov chain
- Using [TensorFlow][tensorflow] to apply RNN

---

1. [Environment](#environment)
    1. [Software](#software)
    1. [Hardware](#hardware)
1. [Todo](#todo)
1. [Installation](#installation)
1. [Usage](#usage)
    1. [pp_aozora.py](#pp_aozorapy)
    1. [wakachi.py](#wakachipy)
    1. [markovify_sentence.py](#markovify_sentencepy)
    1. [rnn_sentence.py](#rnn_sentencepy)
1. [Preprocessing (markovify_sentence.py)](#preprocessing-markovify_sentencepy)
    1. [Aozora Bunko](#aozora-bunko)
        1. [Remove manually](#remove-manually)
        1. [Remove using pp_aozora.py](#remove-using-pp_aozorapy)
        1. [Replace with whitespace](#replace-with-whitespace)

---

## Environment

### Software

- Python 3.6.6 on Miniconda 4.5.4
- Ubuntu 18.04.1 on Windows Subsystem for Linux (Windows 10 Home 1803 (April 2018))

### Hardware

- CPU: Intel [Core i5 7200U](https://ark.intel.com/products/95443/Intel-Core-i5-7200U-Processor-3M-Cache-up-to-3_10-GHz)
- RAM: 8GB
- CPU: AMD [Ryzen 7 1700](https://www.amd.com/ja/products/cpu/amd-ryzen-7-1700)
- RAM: 16GB

## Todo

- [ ] Try on pure Windows
- [ ] Enable function to use word as a token for RNN-based generation
- [ ] Text formatter for [Aozora bunko][aozora]
    - [ ] Convert all hankaku symbols to zenkaku
    - [x] Remove annotation symbols
- [ ] Enable using various engine for word dividing
    - [ ] [Juman++][jumanpp]
        - Juman++ cannot build on WSL
    - [x] [MeCab][mecab]
- [x] Enable saving model for RNN-based generation
- [x] Recurrent Neural Network
    - Based on [this script](https://github.com/0-jam/tf_tutorials/blob/master/text_generation.py)
        - Enabled command-line options
    - It takes very long time for execution ...
        - The text worte in Japanese, precision improves a little by converting all sentences into Katakana
            - `$ mecab -O yomi`
        - It should be executed on GPU
- [x] Multiprocessing
    - The script gets about 2.5x faster when it spawns 4 processes

## Installation

```bash
## wakachi_janome.py
$ pip install janome

## wakachi_mecab.py
# Required packages (Ubuntu)
$ sudo apt install mecab-ipadic-utf8 mecab libmecab-dev
$ pip install mecab-python3
# (Optional) Install additional dictionary for Mecab
$ git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git ~/mecab-ipadic-neologd
$ cd ~/mecab-ipadic-neologd
$ ./bin/install-mecab-ipadic-neologd -n -a
# When you are asked about the installation of mecab-ipadic-NEologd, answer "yes"
[install-mecab-ipadic-NEologd] : Do you want to install mecab-ipadic-NEologd? Type yes or no.
yes

## markovify_sentence.py
# Using pip (recommended)
$ pip install markovify
# Using Conda
$ conda install -c conda-forge markovify

## rnn_sentence.py
$ conda install tensorflow numpy
```

## Usage

Execute with `-h` option when you want to see the help.

### pp_aozora.py

- Preprocessing script for Aozora Bunko
- Enable word dividing with `-e` option
    - This function is also available in `run_pp_aozora.sh`

```bash
$ python pp_aozora.py wagahaiwa_nekodearu_{,noruby_}utf8.txt
$ python pp_aozora.py wagahaiwa_nekodearu_{,wakachi_}utf8.txt -e mecab

# Execute pp_aozora.py for specific directory
$ bash run_pp_aozora.sh -i text/novel_orig/souseki -o text/novel/souseki -e mecab
```

### wakachi.py

- Preprocessing script for Japanese text

```bash
$ python wakachi.py
usage: wakachi.py [-h] input output
wakachi.py: error: the following arguments are required: input, output
$ python wakachi.py wagahaiwa_nekodearu_noruby_utf8.txt wagahaiwa_nekodearu_wakachi_utf8.txt

# Execute wakachi.py for specific directory
$ bash run_wakachi.sh -i text/novel/souseki -o text/novel_wakachi/souseki -m
```

### markovify_sentence.py

```bash
$ python markovify_sentence.py
usage: markovify_sentence.py [-h] [-o OUTPUT] [-n NUMBER] [-j JOBS]
                             [-s STATES]
                             input
markovify_sentence.py: error: the following arguments are required: input
$ python markovify_sentence.py wagahaiwa_nekodearu_wakachi_utf8.txt -o wagahaiwa_nekodearu_markovified_1000.txt -n 100

# Execute markovify_sentence.py for specific directory
$ bash run_markovify.sh
```

### rnn_sentence.py

```bash
$ python rnn_sentence.py
usage: rnn_sentence.py [-h] [-o OUTPUT] [-e EPOCHS] [-g GEN_SIZE]
                       input start_string
rnn_sentence.py: error: the following arguments are required: input, start_string
# No preprocessing needed for input file
$ python rnn_sentence.py souseki_utf8.txt "吾輩" -e 10

# Specifying learned model
# Example: Learned model exists in directory "./learned_models/Latin-Lipsum.txt"
$ ls learned_models/Latin-Lipsum.txt/
Latin-Lipsum.txt.data-00000-of-00001  Latin-Lipsum.txt.index  checkpoint
# Specify the directory name
$ python rnn_sentence.py text/Latin-Lipsum.txt "Lorem " --model learned_models/Latin-Lipsum.txt
```

## Preprocessing (markovify_sentence.py)

- Make sure each words is separated by whitespaces before executing
- In Windows, you will get `UnicodeDecodeError: 'cp932' codec can't decode byte 0x99 in position xxxx` unless input file encoding is not Shift-JIS
- You will get `KeyError: ('\_\_\_BEGIN\_\_', '\_\_\_BEGIN\_\_')` if there is hankaku symbols in the input file

### Aozora Bunko

#### Remove manually

- Title and author
- _【テキスト中に現れる記号について】_ (About symbols in the text)
    - surronded by `-`
- Below _底本：_
- Convert text encoding into UTF-8 by using such as `$ nkf -w` (Text encoding of downloaded file is Shift-JIS)

#### Remove using pp_aozora.py

```
　|^\n+|《.+?》|［.+?］|｜
```

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

[markovify]: https://github.com/jsvine/markovify
[tensorflow]: https://www.tensorflow.org/
[aozora]: https://www.aozora.gr.jp/
[janome]: http://mocobeta.github.io/janome/
[jumanpp]: http://nlp.ist.i.kyoto-u.ac.jp/index.php?JUMAN++
[mecab]: http://taku910.github.io/mecab/
