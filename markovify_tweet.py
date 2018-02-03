### マルコフ連鎖で文章つくって表示
# usage: $ python marcovify_tweet.py <FILENAME>

import sys
import markovify

## ファイル読む
def marcovify_text(file):
    with open(file) as str:
        text = str.read()

    # 読んだテキストを表示
    # print(text)

    ## 読んだテキストからマルコフ連鎖でモデル？生成
    return markovify.Text(text)

model = marcovify_text(sys.argv[1])

for i in range(10):
    # 作ったモデルから適当に文章つくって表示
    print(model.make_sentence())
