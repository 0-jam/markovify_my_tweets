# Regenerate Sentences

- マルコフ連鎖で文章生成
- [markovify][markovify]使用

---

1. [環境](#環境)
1. [Todo](#todo)
1. [インストール](#インストール)
1. [使用法](#使用法)
1. [Note](#note)
    1. [前処理](#前処理)

---

## 環境

- Python 3.6.6 on Miniconda 4.5.4
    - インストールするタイミングによっては，Pythonのバージョンが3.7になっている場合もある
- Ubuntu 18.04.1 on Windows Subsystem for Linux (Windows 10 Home 1803 (April 2018))

## Todo

- [ ] Recurrent Neural Networkに対応
- [ ] [青空文庫](https://www.aozora.gr.jp/)テキスト整形用スクリプト
    - 半角記号を全角にする
    - 注釈記号などの除去
- [x] マルチプロセス化
    - 4プロセスで平均2.5倍くらい速くなった

## インストール

```bash
# pipを使う場合
# Anaconda (Miniconda)環境でもこっちでいいかも
$ pip install janome markovify
# condaを使う場合
$ conda install -c conda-forge markovify
$ pip install janome
```

## 使用法

```bash
## すべてのスクリプトは，-hオプションでヘルプが表示される
# 前処理スクリプト
# デフォルト値は存在せず，入力・出力両方のファイル名を指定しないとエラー
$ python wakachi.py
usage: wakachi.py [-h] input output
wakachi.py: error: the following arguments are required: input, output
$ python wakachi.py wagahaiwa_nekodearu_noruby_utf8.txt wagahaiwa_nekodearu_wakachi_utf8.txt

# 本体
# 出力ファイルのデフォルトはout.txt
$ python markovify_sentence.py
usage: markovify_sentence.py [-h] [-o OUTPUT] [-n NUMBER] [-j JOBS] input
markovify_sentence.py: error: the following arguments are required: input
$ python markovify_sentence.py wagahaiwa_nekodearu_wakachi_utf8.txt -o wagahaiwa_nekodearu_markovified_1000.txt -n 1000

# 一括実行スクリプト
# デフォルトでは./text内のすべての.txtファイルについて1回ずつ文章生成し，その結果を./text/generated_(YYYYMMDD)に保存する
$ bash run.sh
```

## Note

- 実行するときは単語が半角スペースで区切られている必要がある
- Windows環境ではファイルをShift-JISにしないと`UnicodeDecodeError: 'cp932' codec can't decode byte 0x99 in position xxxx`
- 半角記号が文書内にあると`KeyError: ('\_\_\_BEGIN\_\_', '\_\_\_BEGIN\_\_')`

### 前処理

学習対象データに青空文庫を使う場合，不要な文字を除去するために以下の正規表現を使う

```
　|《.+?》|［.+?］|｜|^\n
```

- 全角スペース
    - > 　吾輩は猫である。名前はまだ無い。
- ふりがなとそれが付く文字列の始まりを示す｜（全角縦棒）
    - > しかもあとで聞くとそれは書生という人間中で一番 **｜** 獰悪 **《どうあく》** な種族であったそうだ。
- 注釈
    - > **［＃８字下げ］** 一 **［＃「一」は中見出し］**
- 空行

欧文の始まりを示す以下のかっこは半角スペースに置き換える

```
〔|〕
```

[markovify]: https://github.com/jsvine/markovify
[janome]: http://mocobeta.github.io/janome/
