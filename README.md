# Regenerate Sentences

- マルコフ連鎖やRecurrent Neural Networkで文章生成
- [markovify][markovify]使用
- RNN版は[TensorFlow](https://www.tensorflow.org/)使用

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
        1. [削除](#削除)
        1. [半角スペースに置き換える](#半角スペースに置き換える)

---

## 環境

### ソフトウェア

- Python 3.6.6 on Miniconda 4.5.4
    - インストールするタイミングによっては，Pythonのバージョンが3.7になっている場合もある
- Ubuntu 18.04.1 on Windows Subsystem for Linux (Windows 10 Home 1803 (April 2018))

### ハードウェア

- CPU: Intel [Core i5 7200U](https://ark.intel.com/products/95443/Intel-Core-i5-7200U-Processor-3M-Cache-up-to-3_10-GHz)
- RAM: 8GB
- こっちでも試したい
    - CPU: AMD [Ryzen 7 1700](https://www.amd.com/ja/products/cpu/amd-ryzen-7-1700)
    - RAM: 16GB

## Todo

- [ ] RNN版の分かち書き対応
- [ ] [青空文庫](https://www.aozora.gr.jp/)テキスト整形用スクリプト
    - [ ] 半角記号を全角にする
    - [x] 注釈記号などの除去
- [ ] 分かち書きスクリプトをいろいろなエンジンに対応
    - [ ] [Juman++](http://nlp.ist.i.kyoto-u.ac.jp/index.php?JUMAN++)
        - WSLでビルドできず
    - [x] [MeCab](http://taku910.github.io/mecab/)
- [x] Recurrent Neural Networkに対応
    - [以前書いたもの](https://github.com/0-jam/tf_tutorials/blob/master/text_generation.py)をベースに、コマンドラインオプションに対応
    - 実行にはかなり時間かかるうえ，5-10世代程度ではロクな精度が出ない
        - たぶんデータも足りていないが，これ以上増やすと学習時間どうなるんだ
        - 前処理後のファイルを`$ mecab -O yomi`でカタカナに変換すると多少マシになる
- [x] マルチプロセス化
    - 4プロセスで平均2.5倍くらい速くなった

## インストール

```bash
## wakachi_mecab.py
# 必要パッケージ (Ubuntu)
$ sudo apt install mecab-ipadic-utf8 mecab libmecab-dev
$ pip install mecab-python3
# (Optional) Mecab追加辞書をインストール
$ git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git ~/mecab-ipadic-neologd
$ cd ~/mecab-ipadic-neologd
$ ./bin/install-mecab-ipadic-neologd -n -a
# 途中こう訊かれるので、"yes"と入力
[install-mecab-ipadic-NEologd] : Do you want to install mecab-ipadic-NEologd? Type yes or no.
yes

## markovify_sentence.py
# pipを使う場合（Anacondaでも同じ）
$ pip install janome markovify

## rnn_sentence.py
$ conda install tensorflow numpy
```

## 使用法

すべてのスクリプトは，-hオプションでヘルプが表示される

### pp_aozora.py

- 前処理スクリプト（青空文庫用）
- `-w`オプションを指定すると単語の分かち書きもする
    - 一括実行スクリプト`run_pp_aozora.sh`も同様

```bash
$ python pp_aozora.py
usage: pp_aozora.py [-h] [-w] input output
pp_aozora.py: error: the following arguments are required: input, output
$ python pp_aozora.py wagahaiwa_nekodearu_{,noruby_}utf8.txt
$ python pp_aozora.py wagahaiwa_nekodearu_{,wakachi_}utf8.txt -w

# 一括実行スクリプト
$ bash run_pp_aozora.sh -i text/novel_orig/souseki -o text/novel/souseki
```

### wakachi.py

- 前処理スクリプト（日本語文書用）

```bash
# デフォルト値は存在せず，入力・出力両方のファイル名を指定しないとエラー
$ python wakachi.py
usage: wakachi.py [-h] input output
wakachi.py: error: the following arguments are required: input, output
$ python wakachi.py wagahaiwa_nekodearu_noruby_utf8.txt wagahaiwa_nekodearu_wakachi_utf8.txt
```

### markovify_sentence.py

```bash
# 本体
# 出力ファイルのデフォルトはout.txt
$ python markovify_sentence.py
usage: markovify_sentence.py [-h] [-o OUTPUT] [-n NUMBER] [-j JOBS]
                             [-s STATES]
                             input
markovify_sentence.py: error: the following arguments are required: input
$ python markovify_sentence.py wagahaiwa_nekodearu_wakachi_utf8.txt -o wagahaiwa_nekodearu_markovified_1000.txt -n 1000

# 一括実行スクリプト
# デフォルトでは./text内のすべての.txtファイルについて1回ずつ文章生成し，その結果を./text/generatedに保存する
$ bash run.sh
```

### rnn_sentence.py

```bash
$ python rnn_sentence.py
usage: rnn_sentence.py [-h] [-o OUTPUT] [-e EPOCHS] [-g GEN_SIZE]
                       input start_string
rnn_sentence.py: error: the following arguments are required: input, start_string
# 入力ファイル・開始文字列の順に指定
# テキストに特に前処理は必要ない
$ python rnn_sentence.py souseki_utf8.txt "吾輩" -e 10
```

## 前処理 (markovify_sentence.py)

- 実行するときは単語が半角スペースで区切られている必要がある
- Windows環境ではファイルをShift-JISにしないと`UnicodeDecodeError: 'cp932' codec can't decode byte 0x99 in position xxxx`
- 半角記号が文書内にあると`KeyError: ('\_\_\_BEGIN\_\_', '\_\_\_BEGIN\_\_')`

### 青空文庫

- タイトル・作者・最初のハイフンで囲まれた _【テキスト中に現れる記号について】_ の部分と _底本：_ から下の部分は手動で消すほうがむしろ確実かも…
- ダウンロード時点での文字コードはShift-JISなので、必要に応じて`$ nkf -w`などでUTF-8などに変換する

#### 削除

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
[janome]: http://mocobeta.github.io/janome/
