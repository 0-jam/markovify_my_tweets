# Regenerate Sentences

- マルコフ連鎖で文章つくって表示
- [marcovify](marcovify)モジュールの基本機能なぞっただけ

## Usage

`$ python marcovify_tweet.py <FILENAME>`

[markovify]: https://github.com/jsvine/markovify

## Known Issues

- 文字コード問題
  - Windows環境ではファイルをShift JISにしないと`UnicodeDecodeError: 'cp932' codec can't decode byte 0x99 in position xxxx`と表示されて動かない
