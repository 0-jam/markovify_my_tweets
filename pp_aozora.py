import argparse
import re

## 引数sentenceを整形
def replace_sentence(sentence):
    # 不要な記号を削除
    sentence = re.sub("《.+?》|［.+?］|｜|　", "", sentence.strip())
    # 不要な記号を半角スペースに置換
    sentence = re.sub("〔|〕", " ", sentence)

    return sentence

def replace_text(text):
    # BUG: 入力テキストから空行を削除…できない
    text = list(filter(lambda line: line != "\n", text))
    return [replace_sentence(line) for line in text]

def main():
    # オプション設定・取得
    parser = argparse.ArgumentParser(description="Preprocessing for Aozora Bunko.")
    parser.add_argument("input", type=str, help="input file path")
    parser.add_argument("output", type=str, help="output file path")
    parser.add_argument("-w", "--wakachi", action="store_true", help="enable word dividing")

    args = parser.parse_args()

    with open(args.input) as input:
        text = replace_text(text)

    if args.wakachi:
        from wakachi import divide_text

        text = divide_text(text)

    # 改行区切りでファイルに書き込む
    with open(args.output, 'w') as out:
        out.write("\n".join(text))

if __name__ == '__main__':
    main()