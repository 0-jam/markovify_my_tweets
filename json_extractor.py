import argparse
import json
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="utanet_scraper.pyで抽出した曲情報から特定の項目を抽出")
    parser.add_argument("input", type=str, help="入力ファイル名")
    parser.add_argument("output", type=str, help="出力ファイル名")
    parser.add_argument("-a", "--attribute", type=str, default="lyric", choices=['id', 'title', 'artist', 'lyricist', 'composer', 'lyric'], help="抽出したい項目（デフォルト：'lyric'）")
    args = parser.parse_args()

    with Path(args.input).open(encoding='utf-8') as input:
        results = json.load(input)

    values = []
    if args.attribute == "id":
        values = list(results.keys())
    else:
        for result in results.values():
            values.append(result[args.attribute])

    with Path(args.output).open("w", encoding='utf-8') as out:
        out.write("\n".join(values))

if __name__ == "__main__":
    main()
