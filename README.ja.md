# Regenerate Sentences

- マルコフ連鎖やRecurrent Neural Networkで文章生成
- [markovify][markovify]使用
- RNN版は[TensorFlow][tensorflow]使用

---

1. [環境](#環境)
    1. [ソフトウェア](#ソフトウェア)
    1. [ハードウェア](#ハードウェア)
1. [Todo](#todo)
1. [インストール](#インストール)
1. [使用法](#使用法)
    1. [pp_aozora.py](#pp_aozorapy)
    1. [wakachi.py](#wakachipy)
    1. [markovify_sentence.py](#markovify_sentencepy)
    1. [rnn_sentence.py](#rnn_sentencepy)
1. [前処理 (markovify_sentence.py)](#前処理-markovify_sentencepy)
    1. [青空文庫](#青空文庫)
        1. [手動で削除](#手動で削除)
        1. [pp_aozora.pyで削除](#pp_aozorapyで削除)
        1. [半角スペースに置き換える](#半角スペースに置き換える)

---

## 環境

### ソフトウェア

- [x] Miniconda 4.5.4 (Python 3.6.6) on Ubuntu 18.04.1
- [x] Python 3.6.7 on Ubuntu 18.04.1 on Windows Subsystem for Linux (Windows 10 Home 1803 (April 2018))
- [ ] Python 3.6.7 on Ubuntu 18.04.1
- [ ] Python 3.6.7 on Windows 10 Home 1803 (April 2018)

### ハードウェア

- PC 1
    - CPU: Intel [Core i5 7200U](https://ark.intel.com/products/95443/Intel-Core-i5-7200U-Processor-3M-Cache-up-to-3_10-GHz)
    - RAM: 8GB
- PC 2
    - CPU: AMD [Ryzen 7 1700](https://www.amd.com/ja/products/cpu/amd-ryzen-7-1700)
    - RAM: 16GB
    - [ ] GPU: AMD Radeon RX 580
        - 2304 cores (64 CUs), 8GB VRAM
        - [ROCm](https://github.com/RadeonOpenCompute/ROCm)が必要
        - [公式Dockerイメージ](https://hub.docker.com/r/rocm/tensorflow/)で動作確認済み

## Todo

- [ ] [ベンチマークスクリプト](https://github.com/0-jam/regen_sentence_bm)をこちらに統合
- [ ] ROCmインストール手順書いておこう
- [ ] Windows対応
    - [ ] 文字コード
    - [ ] 学習済みモデルディレクトリ作成
- [ ] RNN版の分かち書き対応
- [ ] [青空文庫][aozora]テキスト整形用スクリプト
    - [ ] 半角記号を全角にする
    - [x] 注釈記号などの除去
- [ ] 分かち書きスクリプトをいろいろなエンジンに対応
    - [ ] [Juman++][jumanpp]
        - WSLでビルドできず
    - [x] [MeCab][mecab]
- [x] RNN版でモデルを保存できるようにする
- [x] Recurrent Neural Networkに対応
    - [これ](https://github.com/0-jam/tf_tutorials/blob/master/text_generation.py)をベースに，コマンドラインオプションに対応
    - 実行にはかなり時間かかるうえ，5-10世代程度ではロクな精度が出ない
        - たぶんデータも足りていないが，これ以上増やすと学習時間どうなるんだ
        - 前処理後のファイルを`$ mecab -O yomi`でカタカナに変換すると多少マシになる
        - GPU使わないとダメか
- [x] マルチプロセス化
    - 4プロセスで平均2.5倍くらい速くなった

## インストール

```bash
# wakachi_janome.py
$ pip install janome

# wakachi_mecab.py
$ sudo apt install mecab-ipadic-utf8 mecab libmecab-dev
$ pip install mecab-python3
# (Optional) Mecab追加辞書をインストール
$ git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git ~/mecab-ipadic-neologd
$ cd ~/mecab-ipadic-neologd
$ ./bin/install-mecab-ipadic-neologd -n -a
# 途中こう訊かれたら"yes"と入力
[install-mecab-ipadic-NEologd] : Do you want to install mecab-ipadic-NEologd? Type yes or no.
yes

# markovify_sentence.py
# pipを使う場合（推奨）
$ pip install markovify
# Condaを使う場合
$ conda install -c conda-forge markovify

# rnn_sentence.py
$ conda install tensorflow numpy
```

## 使用法

すべてのスクリプトは，-hオプションでヘルプが表示される

### pp_aozora.py

- 前処理スクリプト（青空文庫用）
- `-e`オプションにエンジン名を指定すると単語の分かち書きもする
    - 一括実行スクリプト`run_pp_aozora.sh`も同様

```bash
$ python pp_aozora.py wagahaiwa_nekodearu_{,noruby_}utf8.txt
$ python pp_aozora.py wagahaiwa_nekodearu_{,wakachi_}utf8.txt -e mecab

# 指定されたディレクトリに対して実行
$ bash run_pp_aozora.sh -i text/novel_orig/souseki -o text/novel/souseki -e mecab
```

### wakachi.py

- 前処理スクリプト（日本語文書用）

```bash
$ python wakachi.py wagahaiwa_nekodearu_noruby_utf8.txt wagahaiwa_nekodearu_wakachi_utf8.txt

# 指定されたディレクトリに対して実行
$ bash run_wakachi.sh -i text/novel/souseki -o text/novel_wakachi/souseki -m
```

### markovify_sentence.py

```bash
$ python markovify_sentence.py wagahaiwa_nekodearu_wakachi_utf8.txt -o wagahaiwa_nekodearu_markovified_1000.txt -n 100

# 指定されたディレクトリに対して実行
$ bash run.sh
```

### rnn_sentence.py

```bash
$ python rnn_sentence.py
usage: rnn_sentence.py [-h] [-o OUTPUT] [-e EPOCHS] [-g GEN_SIZE]
                       input start_string
rnn_sentence.py: error: the following arguments are required: input, start_string
# 特に前処理は必要ない
$ python rnn_sentence.py souseki_utf8.txt "吾輩" -e 10

# 学習済みモデルを指定
# 例：ディレクトリ"./learned_models/Latin-Lipsum.txt"内にモデルがあるとする
$ ls learned_models/Latin-Lipsum.txt/
Latin-Lipsum.txt.data-00000-of-00001  Latin-Lipsum.txt.index  checkpoint
# ディレクトリ名を指定
$ python rnn_sentence.py text/Latin-Lipsum.txt "Lorem " --model_dir learned_models/Latin-Lipsum.txt/Latin-Lipsum.txt
```

## 前処理 (markovify_sentence.py)

- 実行するときは単語が半角スペースで区切られている必要がある
- Windows環境ではファイルをShift-JISにしないと`UnicodeDecodeError: 'cp932' codec can't decode byte 0x99 in position xxxx`
- 半角記号が文書内にあると`KeyError: ('\_\_\_BEGIN\_\_', '\_\_\_BEGIN\_\_')`

### 青空文庫

#### 手動で削除

- タイトル
- 作者
- _【テキスト中に現れる記号について】_
    - ハイフンで囲まれた部分と
- _底本：_ から下の部分
- ダウンロード時点での文字コードはShift-JISなので，必要に応じて`$ nkf -w`などでUTF-8などに変換する

#### pp_aozora.pyで削除

```
　|^\n+|《.+?》|［.+?］|｜
```

- 行を読んで`strip()`すると消えるもの
    - 全角スペース
        - > 　吾輩は猫である。名前はまだ無い。
    - 1つ以上連続する空行
- ふりがなとそれが付く文字列の始まりを示す｜（全角縦棒）
    - > しかもあとで聞くとそれは書生という人間中で一番 **｜** 獰悪 **《どうあく》** な種族であったそうだ。
- 注釈
    - > **［＃８字下げ］** 一 **［＃「一」は中見出し］**

#### 半角スペースに置き換える

```
〔|〕
```

- 欧文の始まり
    - > 〔Quid aliud est mulier nisi amicitiae& inimica〕

[markovify]: https://github.com/jsvine/markovify
[tensorflow]: https://www.tensorflow.org/
[aozora]: https://www.aozora.gr.jp/
[janome]: http://mocobeta.github.io/janome/
[jumanpp]: http://nlp.ist.i.kyoto-u.ac.jp/index.php?JUMAN++
[mecab]: http://taku910.github.io/mecab/
