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
   1. [前処理スクリプト](#前処理スクリプト)
   1. [テキスト生成スクリプト](#テキスト生成スクリプト)
1. [使用法](#使用法)
   1. [pp_aozora.py](#pp_aozorapy)
   1. [wakachi.py](#wakachipy)
   1. [markovify_sentence.py](#markovify_sentencepy)
   1. [rnn_sentence.py & wrnn_sentence.py & w2v_sentence.py](#rnn_sentencepy--wrnn_sentencepy--w2v_sentencepy)
   1. [bm_rnn_sentence.py](#bm_rnn_sentencepy)
   1. [utanet_scraper.py](#utanet_scraperpy)
   1. [json_extractor.py](#json_extractorpy)
1. [前処理 (markovify_sentence.py)](#前処理-markovify_sentencepy)
   1. [青空文庫](#青空文庫)
      1. [手動で削除](#手動で削除)
      1. [pp_aozora.pyで削除](#pp_aozorapyで削除)
      1. [半角スペースに置き換える](#半角スペースに置き換える)
1. [ベンチマーク](#ベンチマーク)
   1. [データセット](#データセット)
   1. [ルール](#ルール)
   1. [評価基準](#評価基準)
   1. [記録](#記録)

---

## 環境

### ソフトウェア

- Python < 3.7.0
- テスト済みOS
    - Ubuntu 18.04.1 on Windows Subsystem for Linux (Windows 10 Home 1803 (April 2018))
    - Windows 10 Home 1803 (April 2018)
    - Ubuntu 18.04.1 + ROCm 1.9
    - Ubuntu 18.04.1 + CUDA 9.0 + CuDNN 7.4.1.5
- TensorFlow >= 1.11.0 (< 2.0)

### ハードウェア

- CPUはあればあるだけ使ってくれるらしい
- PC 1
    - CPU: Intel [Core i5 7200U](https://ark.intel.com/products/95443/Intel-Core-i5-7200U-Processor-3M-Cache-up-to-3_10-GHz)
    - RAM: 8GB
- PC 2
    - CPU: AMD [Ryzen 7 1700](https://www.amd.com/ja/products/cpu/amd-ryzen-7-1700)
    - RAM: 16GB
    - GPU: AMD Radeon RX 580
        - 2304 cores (64 CUs), 8GB VRAM
        - [ROCm](https://github.com/RadeonOpenCompute/ROCm)が必要
        - [公式Dockerイメージ](https://hub.docker.com/r/rocm/tensorflow/)で動作確認済み
- PC 3
    - CPU: Intel [Core i5-8400](https://ark.intel.com/ja/products/126687/Intel-Core-i5-8400-Processor-9M-Cache-up-to-4-00-GHz-)
    - RAM: 16GB
    - GPU: NVIDIA [Geforce RTX 2080](https://www.nvidia.com/ja-jp/geforce/graphics-cards/rtx-2080/)
    - VRAM: 8GB
    - OS: Ubuntu 18.04.1
        - CUDA 9.0

## Todo

- [ ] RNN版の訓練とテキスト生成を分離
    - ~~"生成だけする"オプションを追加するほうがいいかも~~
- [ ] RNNテキスト生成いろいろ整理
- [ ] 歌ネットスクレイパーの検索条件
    - 例：
        - アーティスト名
        - 複数条件対応
        - 抽出件数
- [x] word2vecモデル
- [x] RNN版の分かち書き対応
- [x] 分かち書きスクリプトをいろいろなエンジンに対応
    - [x] [Juman++][jumanpp]
        - WSLでビルドできず
    - [x] [MeCab][mecab]
- [x] [青空文庫][aozora]テキスト整形用スクリプト
    - [x] タイトル，作者名，底本除去
    - [x] 注釈記号などの除去
- [x] Windows対応
    - [x] 文字コード
    - [x] 学習済みモデルディレクトリ作成
        - >ValueError: Parent directory of C:\path\of\repo\regen_my_sentences\learned_models\Latin-Lipsum.txt\Latin-Lipsum.txt doesn't exist, can't save.
- [x] [ベンチマークスクリプト](https://github.com/0-jam/regen_sentence_bm)をこちらに統合
    - [x] スクリプト
    - [x] データセット
        - 自分のGoogle Driveからダウンロードするようにした
    - [x] README
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

### 前処理スクリプト

- [Juman++ダウンロードページ][jumanpp]
- `json_extractor.py`に外部モジュールは必要ない

```bash
# 共通
$ pip install tqdm

### wakachi.py
## Janomeを分かち書きエンジンに使う場合
$ pip install janome

## MeCabを分かち書きエンジンに使う場合
$ sudo apt install mecab-ipadic-utf8 mecab libmecab-dev swig
$ pip install mecab-python3
# （任意，Linuxのみ）Mecab追加辞書をインストール
$ git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git ~/mecab-ipadic-neologd
$ cd ~/mecab-ipadic-neologd
$ ./bin/install-mecab-ipadic-neologd -n -a -y

## Juman++を分かち書きエンジンに使う場合
# Juman++をインストール
# tarballを公式ページ（上記）からダウンロードし，それを展開して展開先のディレクトリに入る
$ ./configure --prefix=$HOME/.local
$ make -j$(nproc)
$ make install
$ pip install pyknp
$ export PATH="$HOME/.local/bin:$PATH"

### utanet_scraper.py
$ pip install beautifulscraper
```

### テキスト生成スクリプト

```bash
## markovify_sentence.py
$ pip install markovify

## rnn_sentence.py, bm_rnn_sentence.py, wrnn_sentence.py
# pyenv環境ではPythonビルド前にLZMAライブラリのヘッダーをインストールする必要がある
$ sudo apt install liblzma-dev
$ pyenv install 3.6.8
# NVIDIA GPUを持っていて，CUDAで計算できるようにしたかったらtensorflowではなくtensorflow-gpuをインストール
$ pip install tensorflow numpy matplotlib
## w2v_sentence.py
$ pip install gensim
```

## 使用法

すべてのスクリプトは，-hオプションでヘルプが表示される

### pp_aozora.py

- 前処理スクリプト（青空文庫用）
- ~~`-e`オプションにエンジン名を指定すると単語の分かち書きもする~~ 一時的に削除
    - ~~一括実行スクリプト`run_pp_aozora.sh`も同様~~

```bash
$ python pp_aozora.py wagahaiwa_nekodearu_{,noruby_}utf8.txt
$ python pp_aozora.py wagahaiwa_nekodearu_{,wakachi_}utf8.txt

# 指定されたディレクトリに対して実行
$ bash run_pp_aozora.sh -i text/novel_orig/souseki -o text/novel/souseki
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
# "-o"オプションにファイル名を指定すると生成された文章が保存される
$ python markovify_sentence.py souseki_wakachi.txt -n 100
```

### rnn_sentence.py & wrnn_sentence.py & w2v_sentence.py

```bash
# "--cpu_mode"オプションをつけると強制的にCuDNNでないGRU Layerを使った学習になる
# 文字ベースの学習
# 特に前処理は必要ない
$ python rnn_sentence.py souseki_utf8.txt "吾輩" -e 10

# 単語ベースの学習
# 事前に分かち書きをしておく必要がある
$ python wrnn_sentence.py souseki_wakachi.txt "吾輩" -e 10

# 学習済みモデルを指定
# 例：ディレクトリ"./learned_models/Latin-Lipsum.txt"内にモデルがあるとする
$ ls learned_models/Latin-Lipsum.txt/
Latin-Lipsum.txt.data-00000-of-00001  Latin-Lipsum.txt.index  checkpoint
# ディレクトリ名を指定
# モデルの訓練はスキップされる
$ python rnn_sentence.py text/Latin-Lipsum.txt "Lorem " --model_dir learned_models/Latin-Lipsum.txt
```

### bm_rnn_sentence.py

```bash
# これだけ
$ python bm_rnn_sentence.py
```

### utanet_scraper.py

- [歌ネット](https://www.uta-net.com/)で作詞家を検索して曲情報を抽出
- 抽出結果はJSONで保存される
    - key: song_id（抽出元のURL）
    - values:
        - title（曲名）
        - artist（歌手名）
        - lyricist（作詞者名）
        - composer（作曲者名）
        - lyric（歌詞）

```bash
# 抽出されたテキストはデフォルトで"songs.json"に保存される
$ python utanet_scraper.py "秋元康"
```

### json_extractor.py

- 指定した属性を[utanet_scraper.py](#utanet_scraperpy)で出力したJSONから抽出
    - Specifing multiple attributes are **not** available
- 抽出された属性はテキストで保存される
    - 曲ごとに改行
- 指定できる属性：
    - 'id'
    - 'title'
    - 'artist'
    - 'lyricist'
    - 'composer'
    - 'lyric'

```bash
# デフォルトの属性：lyrics
$ python json_extractor.py akimoto.json akimoto_lyrics.txt
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

- bm_rnn_sentence.py: rnn_sentence.pyベースのベンチマークスクリプト
    - 基本的にオリジナルの機能を大きく省いただけ
- 1時間（仮）で何epoch学習できて，そのモデルから20行生成した時にどの程度読める文章ができるかを比較

### データセット

- 夏目漱石の小説7編
    1. 坊っちゃん
    1. こころ
    1. 草枕
    1. 思い出す事など
    1. 三四郎
    1. それから
    1. 吾輩は猫である
- [この方法](#青空文庫)で前処理済
    - [青空文庫](https://www.aozora.gr.jp/index_pages/person148.html)がベース
- 前処理後にXZで圧縮
    - スクリプト実行時にPythonによって展開される
    - 展開後サイズ：約3.01MiB
    - 圧縮：`$ xz -9 -e -T 0 souseki_utf8.txt`
    - 展開：`$ xz -d souseki_utf8.txt -k`

### ルール

1. モデルの学習が始まった瞬間から計測スタート
1. あらかじめ決められた時間の間学習を続ける
1. 決められた時間を超過した場合，そのepochを終えた段階で学習を終了する
    - 例：制限時間15分
        - epoch数3の学習中に15分経過した場合，epoch3の学習を終えて終了
    - 制限時間内に _50（仮）_ epoch学習できた場合，経過時間にかかわらず学習を終了
1. 結果を表示
    - 所要時間
    - epoch数
    - 上二つから計算できる1分あたりのepoch数
    - loss（損失関数）の値
    - モデルから生成されたテキスト
        - 20行

### 評価基準

- 何epoch学習できたか？
    - 1epochあたりにかかった時間は？
- loss（損失関数）の値は？
    - 小さければ小さいほど _まともな_ 文章が生成される…はず

### 記録

- ベンチマーク記録は[こちら](https://gist.github.com/0-jam/f21f44375cb70b987e99cda485d6940d)

[markovify]: https://github.com/jsvine/markovify
[tensorflow]: https://www.tensorflow.org/
[aozora]: https://www.aozora.gr.jp/
[janome]: http://mocobeta.github.io/janome/
[jumanpp]: http://nlp.ist.i.kyoto-u.ac.jp/index.php?JUMAN++
[mecab]: http://taku910.github.io/mecab/
