# Regenerate Sentences

- マルコフ連鎖で文章つくって表示
- [markovify][markovify]モジュールの基本機能なぞっただけ

## Environment

- Python 3.6.6 on Miniconda 4.5.4
- Ubuntu 18.04.1 on Windows Subsystem for Linux (Windows 10 Home 1803 (April 2018))
- Python 3.7
- Windows 10 Home 1803 (April 2018)

## Todo

- [ ] Recurrent Neural Networkに対応
- [ ] 青空文庫テキスト整形用スクリプト
    - 半角記号を全角にする
    - 注釈記号などの除去

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

## Note

- 半角記号は全角にしないとエラー
    - > KeyError: ('\_\_\_BEGIN\_\_', '\_\_\_BEGIN\_\_')
- 学習対象データに青空文庫を使う場合、不要な文字を除去するために以下の正規表現を使う
    - 段落などを示す全角スペース
    - 獰悪《どうあく》のようなルビ
    - ［＃ここから2字下げ］のような注釈
    - ルビの付く文字列の始まりを示す｜（全角縦棒）
    - 空行

```
　|《.+?》|［.+?］|｜|^\n
```

[markovify]: https://github.com/jsvine/markovify
[janome]: http://mocobeta.github.io/janome/
