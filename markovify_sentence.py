import sys
import markovify

## ファイル読んでマルコフ連鎖モデル作成
def marcovify_text(file):
    with open(file) as str:
        text = str.read()

    return markovify.Text(text)

model = marcovify_text(sys.argv[1])

with open('out.txt', 'w') as out:
    arr = []
    for i in range(10):
        # 作ったモデルから文章生成
        arr.append(model.make_sentence())

    # カラ(NoneType)の要素を削除
    arr = list(filter(None, arr))
    # ファイルに書き込む
    out.write("\n".join(arr))
