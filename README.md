# Regenerate Sentences

- マルコフ連鎖で文章つくって表示
- [markovify][markovify]モジュールの基本機能なぞっただけ

## Environment

- Python 3.6.6 on Miniconda 4.5.4
- Ubuntu 18.04.1 on Windows Subsystem for Linux (Windows 10 Home 1803 (April 2018))
- Python 3.7
- Windows 10 Home 1803 (April 2018)

## Todo

- Recurrent Neural Networkに対応

## Installation

```bash
# pipを使う場合
# Anaconda (Miniconda)環境でもこっちでいいかも
$ pip install janome markovify
# condaを使う場合
$ conda install -c conda-forge markovify
$ pip install janome
```

## Usage

- 引数ないときの動作は未実装

`$ python markovify_tweet.py <FILENAME>`

[Janome][janome]を用いた前処理用スクリプト：`./wakachi.py`

`$ python wakachi.py <FILENAME> <OUTPUT_FILE>`

## Known Issues

- 文字コード問題
    - Windows環境ではファイルをShift JISにしないと`UnicodeDecodeError: 'cp932' codec can't decode byte 0x99 in position xxxx`と表示されて動かない
- 日本語を学習してくれない
    - ロジックとか自分で書くべきだろうか

[markovify]: https://github.com/jsvine/markovify
[janome]: http://mocobeta.github.io/janome/
