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
   1. [Preprocessing scripts](#preprocessing-scripts)
   1. [Text generating scripts](#text-generating-scripts)
1. [Usage](#usage)
   1. [pp_aozora.py](#pp_aozorapy)
   1. [wakachi.py](#wakachipy)
   1. [markovify_sentence.py](#markovify_sentencepy)
   1. [rnn_sentence.py](#rnn_sentencepy)
   1. [bm_rnn_sentence.py](#bm_rnn_sentencepy)
   1. [utanet_scraper.py](#utanet_scraperpy)
   1. [json_extractor.py](#json_extractorpy)
1. [Preprocessing (markovify_sentence.py)](#preprocessing-markovify_sentencepy)
   1. [Aozora Bunko](#aozora-bunko)
      1. [Remove manually](#remove-manually)
      1. [Remove using pp_aozora.py](#remove-using-pp_aozorapy)
      1. [Replace with whitespace](#replace-with-whitespace)
1. [Benchmarking](#benchmarking)
   1. [About Dataset](#about-dataset)
   1. [Rule](#rule)
   1. [Evaluation](#evaluation)
   1. [Records](#records)
1. [Troubleshooting](#troubleshooting)

---

## Environment

### Software

- Python < 3.7.0
- Tested OSs
    - Ubuntu 18.04.1 on Windows Subsystem for Linux (Windows 10 Home 1803 (April 2018))
    - Windows 10 Home 1803 (April 2018)
    - Ubuntu 18.04.1 + ROCm 1.9
    - Ubuntu 18.04.1 + CUDA 9.0 + CuDNN 7.4.1.5
- TensorFlow >= 1.11.0 (< 2.0)

### Hardware

- It seems TensorFlow uses CPU as many as possible
- PC 1
    - CPU: Intel [Core i5 7200U](https://ark.intel.com/products/95443/Intel-Core-i5-7200U-Processor-3M-Cache-up-to-3_10-GHz)
    - RAM: 8GB
- PC 2
    - CPU: AMD [Ryzen 7 1700](https://www.amd.com/ja/products/cpu/amd-ryzen-7-1700)
    - RAM: 16GB
    - GPU: AMD Radeon RX 580
        - 2304 cores (64 CUs), 8GB VRAM
        - It requires [ROCm](https://github.com/RadeonOpenCompute/ROCm)
        - Script executed successfully by using [official Docker image](https://hub.docker.com/r/rocm/tensorflow/)
- PC 3
    - CPU: Intel [Core i5-8400](https://ark.intel.com/ja/products/126687/Intel-Core-i5-8400-Processor-9M-Cache-up-to-4-00-GHz-)
    - RAM: 16GB
    - GPU: NVIDIA [Geforce RTX 2080](https://www.nvidia.com/ja-jp/geforce/graphics-cards/rtx-2080/)
    - VRAM: 8GB
    - OS: Ubuntu 18.04.1
        - CUDA 9.0

## Todo

- [ ] Separate RNN trainer and generator
- [ ] Add search options to Utanet scraper
    - Example:
        - Artist name
        - Enable multiple search options
        - Number of songs to extract
- [ ] Add ROCm instruction in this README
- [ ] Add CUDA instruction in this README
- [ ] Enable function to use word as a token for RNN-based generation
- [x] Enable using various engine for word dividing
    - [x] [Juman++][jumanpp]
        - Juman++ cannot build on WSL
    - [x] [MeCab][mecab]
- [x] Separate RNN trainer and generator
    - Adding "generation-only" option seems better...
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
    - Based on [this script](https://github.com/0-jam/tf_tutorials/blob/master/text_generation.py)
        - Enabled command-line options
    - It takes very long time for execution ...
        - The text worte in Japanese, precision improves a little by converting all sentences into Katakana
            - `$ mecab -O yomi`
        - It should be executed on GPU
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
$ git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git ~/mecab-ipadic-neologd
$ cd ~/mecab-ipadic-neologd
$ ./bin/install-mecab-ipadic-neologd -n -a
# When you are asked about the installation of mecab-ipadic-NEologd, answer "yes"
[install-mecab-ipadic-NEologd] : Do you want to install mecab-ipadic-NEologd? Type yes or no.
yes

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

## rnn_sentence.py & bm_rnn_sentence.py
# If you use pyenv, install liblzma header before building Python
$ sudo apt install liblzma-dev
$ pyenv install 3.6.7
# If you have NVIDIA GPU, install tensorflow-gpu instead of tensorflow to enable CUDA-based computing
$ pip install tensorflow numpy matplotlib
```

## Usage

Execute with `-h` option when you want to see the help.

### pp_aozora.py

- Preprocessing script for Aozora Bunko
- Enable word dividing with `-e` option
    - This function is also available in `run_pp_aozora.sh`

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

### rnn_sentence.py

```bash
# No preprocessing needed for input file
# If you want to force to use Non-CuDNN GRU layer, give "--cpu_mode" option
$ python rnn_sentence.py souseki_utf8.txt "吾輩" -e 10

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

- Do scraping and extract song informations by the lyricist name from [Utanet（歌ネット）](https://www.uta-net.com/)
- Song information is saved as JSON
    - key: song_id from original URL
    - values:
        - title
        - artist
        - lyricist
        - composer
        - lyric

```bash
# Extracted song information is saved as "songs.json" by default
$ python utanet_scraper.py "秋元康"
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

## Preprocessing (markovify_sentence.py)

- Make sure each words is separated by whitespaces before executing
- In Windows, you will get `UnicodeDecodeError: 'cp932' codec can't decode byte 0x99 in position xxxx` unless input file encoding is not Shift-JIS
- You will get `KeyError: ('\_\_\_BEGIN\_\_', '\_\_\_BEGIN\_\_')` if there is hankaku symbols in the input file

### Aozora Bunko

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

- bm_rnn_sentence.py: Benchmarking script based on rnn_sentence.py
    - Almost all functions have been removed from the original script
- Learn specified dataset _in 1 hours(TBD)_, and compare the performance

### About Dataset

- 7 novels written by Souseki Natsume（夏目漱石）
    1. 坊っちゃん (Bocchan)
    1. こころ (Kokoro)
    1. 草枕 (Kusamakura)
    1. 思い出す事など (Omoidasu koto nado)
    1. 三四郎 (Sanshiro)
    1. それから (Sorekara)
    1. 吾輩は猫である (Wagahai wa neko de aru)
- Based on [Aozora Bunko](https://www.aozora.gr.jp/index_pages/person148.html)
    - Already preprocessed by [this](#aozora-bunko) method
- Dataset is XZ-compressed
    - Extract automatically when execute
    - About 3.01MiB after decompressing
    - Compress: `$ xz -9 -e -T 0 souseki_utf8.txt`
    - Extract: `$ xz -d souseki_utf8.txt -k`

### Rule

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

### Evaluation

- How many epochs did the system learned?
    - How many times per epoch?
- What loss function's value?
    - The smaller loss function's value, the more _readable_ sentence can be generated ...probably

### Records

- Records of benchmarking is [here](https://gist.github.com/0-jam/f21f44375cb70b987e99cda485d6940d)

## Troubleshooting

If you got "W tensorflow/core/framework/allocator.cc:122] Allocation of xxx exceeds xx% of system memory." and TensorFlow was killed in `rnn_sentence.py`,
try to give `--no_point_saving` option.

[markovify]: https://github.com/jsvine/markovify
[tensorflow]: https://www.tensorflow.org/
[aozora]: https://www.aozora.gr.jp/
[janome]: http://mocobeta.github.io/janome/
[jumanpp]: http://nlp.ist.i.kyoto-u.ac.jp/index.php?JUMAN++
[mecab]: http://taku910.github.io/mecab/
