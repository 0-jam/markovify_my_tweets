from janome.tokenizer import Tokenizer
import argparse

# 分かち書き用トークナイザ
t = Tokenizer(wakati=True)

## 文sentenceを分かち書き
# delimiter（デフォルトは半角スペース）で単語どうしをつなぐ
def divide_word(sentence, delimiter=" "):
    return delimiter.join(
        list(filter(
            lambda line: line != " ", t.tokenize(sentence.strip())
        ))
    )

## 複数行の（iterableな）テキストtextを分かち書き
# 戻り値は行単位で要素に別れたlist
def divide_text(text, delimiter=" "):
    # 入力テキストから空行を削除
    # divide_word()内で消そうとするとうまくいかない
    text = list(filter(lambda line: line != "\n", text))
    return [divide_word(line, delimiter=delimiter) for line in text]

def main():
    parser = argparse.ArgumentParser(description="<WIP> Preprocessing script for Japanese text.")
    parser.add_argument("input", type=str, help="input file path")
    parser.add_argument("output", type=str, help="output file path")

    args = parser.parse_args()

    with open(args.input) as input:
        text = divide_text(input.readlines())

    # 改行区切りでファイルに書き込む
    with open(args.output, 'w') as out:
        out.write("\n".join(text))

if __name__ == '__main__':
    main()
