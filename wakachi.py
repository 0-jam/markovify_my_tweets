### 前処理用スクリプト
# Janomeを使って読み込んだ文章を分かち書き

import sys
from janome.tokenizer import Tokenizer

# 分かち書き用トークナイザ
t = Tokenizer(wakati=True)

arr = []

with open(sys.argv[1]) as str:
    arr.append(t.tokenize(str.read()))

with open(sys.argv[2], 'w') as out:
    for str in arr:
        out.write(" ".join(str))
