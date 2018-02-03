# Regenerate Sentences

- マルコフ連鎖で文章つくって表示
- [marcovify](marcovify)モジュールの基本機能なぞっただけ

## Usage

- 引数ないときの動作は未実装

`$ python marcovify_tweet.py <FILENAME>`

[Janome][janome]を用いた前処理用スクリプト：`./wakachi.py`

`$ python wakachi.py <FILENAME> <OUTPUT_FILE>`

## Known Issues

- 文字コード問題
  - Windows環境ではファイルをShift JISにしないと`UnicodeDecodeError: 'cp932' codec can't decode byte 0x99 in position xxxx`と表示されて動かない
- 日本語を学習してくれない
  - ロジックとか自分で書くべきだろうか

[markovify]: https://github.com/jsvine/markovify
[janome]: http://mocobeta.github.io/janome/
