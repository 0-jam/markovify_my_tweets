# Regenerate Sentences

- マルコフ連鎖やRecurrent Neural Networkで文章生成
- [markovify][markovify]使用
- RNN版は[TensorFlow][tensorflow]使用

---

1. [環境](#環境)
    1. [ソフトウェア](#ソフトウェア)
1. [インストール（共通）](#インストール共通)
    1. [pip モジュール](#pip-モジュール)
1. [インストール (Ubuntu 18.04)](#インストール-ubuntu-1804)
    1. [分かち書きエンジン](#分かち書きエンジン)
        1. [MeCab](#mecab)
        1. [（未使用）Juman++](#未使用juman)
    1. [テキスト生成](#テキスト生成)
1. [インストール (Arch Linux)](#インストール-arch-linux)
    1. [分かち書きエンジン](#分かち書きエンジン-1)
    1. [テキスト生成](#テキスト生成-1)
1. [使用法](#使用法)
    1. [pp_aozora.py](#pp_aozorapy)
    1. [markovify_sentence.py](#markovify_sentencepy)
    1. [rnn_sentence.py](#rnn_sentencepy)
    1. [classify_lyric.py](#classify_lyricpy)
1. [前処理 (markovify_sentence.py)](#前処理-markovify_sentencepy)
    1. [青空文庫](#青空文庫)
        1. [手動で削除](#手動で削除)
        1. [pp_aozora.pyで削除](#pp_aozorapyで削除)
        1. [半角スペースに置き換える](#半角スペースに置き換える)
1. [ベンチマーク](#ベンチマーク)

---

## 環境

### ソフトウェア

- Python 3.7.4
- テスト済みOS
    - Ubuntu 18.04.2 (Linux 4.18.0) + ROCm 2.6
    - Ubuntu 18.04.2 (Linux 4.18.0 + NVIDIA 410.48) + CUDA 10.0 + CuDNN 7.5.0.56
    - Arch Linux (Linux 5.3.7 + NVIDIA 435.21) + CUDA 10.1.243 + CuDNN 7.6.4.38
- TensorFlow 2.0.0
    - …deprecation warningがたくさん出るが

## インストール（共通）

### pip モジュール

```
$ pipenv install
```

## インストール (Ubuntu 18.04)

### 分かち書きエンジン

- [Juman++ダウンロードページ][jumanpp]

#### MeCab

```
$ sudo apt install mecab-ipadic-utf8 mecab libmecab-dev swig
```

（任意）Mecab追加辞書をインストール

```
$ sudo apt install curl
$ git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git ~/mecab-ipadic-neologd
$ cd ~/mecab-ipadic-neologd
$ ./bin/install-mecab-ipadic-neologd -n -a -y
```

#### （未使用）Juman++

tarballを公式ページ（上記）からダウンロードし，それを展開して展開先のディレクトリに入る

```
$ ./configure --prefix=$HOME/.local
$ make -j$(nproc)
$ make install
$ pip install pyknp
$ export PATH="$HOME/.local/bin:$PATH"
```

### テキスト生成

```bash
## rnn_sentence.py
# pyenv環境ではPythonビルド前にliblzmaのヘッダーをインストールする必要がある
$ sudo apt install liblzma-dev
$ pyenv install 3.7.4
# NVIDIA GPUを持っていて，CUDAで計算できるようにしたかったらtensorflowではなくtensorflow-gpuをインストール
# AMD GPUを持っていて，HIP + MIOpenで計算できるようにしたかったらtensorflowではなくtensorflow-rocmをインストール
$ pip install tensorflow numpy matplotlib
```

## インストール (Arch Linux)

- AURヘルパーにyayを使用

### 分かち書きエンジン

```bash
## MeCabを分かち書きエンジンに使う場合
$ yay -S mecab mecab-ipadic-neologd-git
$ pip install --user mecab-python3
# （任意）Mecab追加辞書をインストール
# Ubuntuと同じようにやっても可
$ yay -S mecab-ipadic-neologd-git
```

### テキスト生成

```bash
## rnn_sentence.py
# NVIDIA GPUを持っていて，CUDAで計算できるようにしたかったらpython-tensorflowではなくpython-tensorflow-cudaをインストール
$ yay -S python-tensorflow-cuda
$ pip install --user matplotlib
## classify_lyric.py
$ pip install --user gensim
```

## 使用法

すべてのスクリプトは，-hオプションでヘルプが表示される

### pp_aozora.py

- 前処理スクリプト（青空文庫用）

```bash
$ python pp_aozora.py wagahaiwa_nekodearu_{,noruby_}utf8.txt

# 指定されたディレクトリに対して実行
$ bash run_pp_aozora.sh -i text/novel_orig/souseki -o text/novel/souseki
```

### markovify_sentence.py

```bash
# "-o"オプションにファイル名を指定すると生成された文章が保存される
# "-c"オプションをつけると文字ベースでの学習になる
$ python markovify_sentence.py souseki_wakachi.txt
```

### rnn_sentence.py

- [これ](https://github.com/0-jam/tf_tutorials/blob/master/text_generation.py)がベース
- GPUが使える環境での実行を推奨

```bash
# start_stringを指定しなかった場合，テキスト内のランダムに選ばれた文字/単語から生成が始まる
# "-w"オプションをつけると単語ベースでの学習になる
$ python rnn_sentence.py souseki_utf8.txt --start_string "吾輩" -e 10

# 学習済みモデルを指定
# 例：ディレクトリ"./learned_models/Latin-Lipsum.txt"内にモデルがあるとする
$ ls learned_models/Latin-Lipsum/
Latin-Lipsum.data-00000-of-00001  Latin-Lipsum.index  checkpoint
# ディレクトリ名を指定
# モデルの訓練はスキップされる
$ python rnn_sentence.py text/Latin-Lipsum.txt --load_dir learned_models/Latin-Lipsum
```

### classify_lyric.py

- 生成されたテキストをアーティスト名や作詞者名で分類
- [doc2vec](https://radimrehurek.com/gensim/models/doc2vec.html)を使用

```bash
# --d2vmodel オプションを指定すると訓練済みのdoc2vecモデルを使える
$ python classify_lyric.py text/lyrics_all.json generated_texts/aki_kosoado_512.txt
```

## 前処理 (markovify_sentence.py)

- 実行するときは単語が半角スペースで区切られている必要がある
- Windows環境ではファイルをShift-JISにしないと`UnicodeDecodeError: 'cp932' codec can't decode byte 0x99 in position xxxx`
- 半角記号が文書内にあると`KeyError: ('\_\_\_BEGIN\_\_', '\_\_\_BEGIN\_\_')`

### 青空文庫

- すべての全角英数字，丸括弧（），全角スペース　，！，？などをそれぞれ半角に置換
    - `unicodedata.normalize('NFKC', text)`

#### 手動で削除

- タイトル
- 作者
- ダウンロード時点での文字コードはShift-JISなので，必要に応じて`$ nkf -w`などでUTF-8などに変換する

#### pp_aozora.pyで削除

```python
# テキスト全体に適用
regex1 = "---.*---\n|底本：.*"
# 1行ずつ読んだものに適用
regex2 = "　|^\n+|《.+?》|［.+?］|｜"
```

- _【テキスト中に現れる記号について】_
- _底本：_ の部分
- テキストを読んで`split()`すると消えるもの
    - 全角スペース
        - > 　吾輩は猫である。名前はまだ無い。
    - すべての改行コード
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

## ベンチマーク

- [0-jam/regen_sentence_bm](https://github.com/0-jam/regen_sentence_bm) に移動した
- 過去のベンチマーク記録は[こちら](https://gist.github.com/0-jam/f21f44375cb70b987e99cda485d6940d)

[markovify]: https://github.com/jsvine/markovify
[tensorflow]: https://www.tensorflow.org/
[aozora]: https://www.aozora.gr.jp/
[janome]: http://mocobeta.github.io/janome/
[jumanpp]: http://nlp.ist.i.kyoto-u.ac.jp/index.php?JUMAN++
[mecab]: http://taku910.github.io/mecab/
