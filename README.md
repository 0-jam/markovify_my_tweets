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
- Ubuntu 18.04.1 on Windows Subsystem for Linux (Windows 10 Home 1803 (April 2018))
- Python 3.7
- Windows 10 Home 1803 (April 2018)

## Todo

- [ ] Recurrent Neural Networkに対応
- [ ] [青空文庫](https://www.aozora.gr.jp/)テキスト整形用スクリプト
    - 半角記号を全角にする
    - 注釈記号などの除去

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

- 引数ないとエラー`IndexError: list index out of range`

`$ python markovify_tweet.py <FILENAME>`

- [Janome][janome]を用いた日本語テキスト前処理用スクリプト：`./wakachi.py`

`$ python wakachi.py <FILENAME> <OUTPUT_FILE>`

## Note

- 文字コード問題
    - Windows環境ではファイルをShift JISにしないと`UnicodeDecodeError: 'cp932' codec can't decode byte 0x99 in position xxxx`と表示されて動かない
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
