import sys
from janome.tokenizer import Tokenizer

# 分かち書き用トークナイザ
t = Tokenizer(wakati=True)

arr = []

# 読み込んだ文章を分かち書き
with open(sys.argv[1]) as str:
    arr.append(t.tokenize(str.read()))

# 半角スペース区切りでファイルに書き込む
with open(sys.argv[2], 'w') as out:
    for str in arr:
        out.write(" ".join(str))
