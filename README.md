# Regenerate Sentences

- マルコフ連鎖で文章生成
- [markovify][markovify]使用

---

1. [環境](#環境)
1. [Todo](#todo)
1. [インストール](#インストール)
1. [使用法](#使用法)
1. [Note](#note)

---

## 環境

- Python 3.6.6 on Miniconda 4.5.4
    - インストールするタイミングによっては、Pythonのバージョンが3.7になっている場合もある
- Ubuntu 18.04.1 on Windows Subsystem for Linux (Windows 10 Home 1803 (April 2018))

## Todo

- [ ] Recurrent Neural Networkに対応
- [ ] [青空文庫](https://www.aozora.gr.jp/)テキスト整形用スクリプト
    - 半角記号を全角にする
    - 注釈記号などの除去
- [ ] マルチスレッドにできないかな？

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
# 前処理スクリプト
$ python wakachi.py
usage: wakachi.py [-h] input output
wakachi.py: error: the following arguments are required: input, output
$ python wakachi.py wagahaiwa_nekodearu_noruby_utf8.txt wagahaiwa_nekodearu_wakachi_utf8.txt

# 本体
$ python markovify_sentence.py
usage: markovify_sentence.py [-h] [-o OUTPUT] [-n NUMBER] input
markovify_sentence.py: error: the following arguments are required: input
$ python markovify_sentence.py wagahaiwa_nekodearu_wakachi_utf8.txt -o wagahaiwa_nekodearu_markovified_1000.txt -n 1000
```

## Note

- 実行するときは単語が半角スペースで区切られている必要がある
- 文字コード問題
    - Windows環境ではファイルをShift-JISにしないと`UnicodeDecodeError: 'cp932' codec can't decode byte 0x99 in position xxxx`
- 半角記号は全角にしないとエラー
    - > KeyError: ('\_\_\_BEGIN\_\_', '\_\_\_BEGIN\_\_')
- 学習対象データに青空文庫を使う場合、不要な文字を除去するために以下の正規表現を使う
    - 段落などを示す全角スペース
    - 獰悪《どうあく》のようなふりがな
    - ［＃ここから2字下げ］のような注釈
    - ふりがなの付く文字列の始まりを示す｜（全角縦棒）
    - 空行

```
　|《.+?》|［.+?］|｜|^\n
```

[markovify]: https://github.com/jsvine/markovify
[janome]: http://mocobeta.github.io/janome/
