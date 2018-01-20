### マルコフ連鎖で文章つくって表示
# usage: $ python marcovify_tweet.py

import sys
import markovify

## ファイル読む
# TODO: 引数で指定できるようにする
with open("Latin-Lipsum.txt") as tweets:
  text = tweets.read()

# 読んだテキストを表示
# print(text)

## 読んだテキストからマルコフ連鎖でモデル？生成
model = markovify.Text(text)

for i in range(10):
  # 作ったモデルから適当に文章つくって表示
  # BUG: たまに"None"になる（データ量足りてない？）
  print(model.make_sentence())
