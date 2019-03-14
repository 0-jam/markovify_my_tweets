import argparse
import json
from pathlib import Path
from modules.multi_sub import replace_str
import unicodedata

def normalize(text):
    # すべての全角英数字，丸カッコ（），全角スペース　，！，？などをそれぞれ半角に置換
    text = unicodedata.normalize('NFKC', text)
    # 3つ以上続くピリオド..., 全角ピリオド・・・を三点リーダー…に置換
    # （上記normalize()で三点リーダーがピリオド3つに置換されているのをここで戻している）
    # 2回以上続く三点リーダー……を1つ…にする
    # 波ダッシュ〜（上記normalize()で半角~に変換済み）をダッシューに置換
    # すべてのカッコ{}[]()<>を丸カッコ()に統一
    # 各要素：(置換したい文字, 置換先の文字)
    patterns = [(r'\.{3,}', '…'), (r'・{3,}', '…'), (r'…{2,}', '…'), (r'~', 'ー'), (r'\[|{|<', '\('), (r'\]|}|>', '\)')]
    text = replace_str(text, patterns)

    return text

def main():
    parser = argparse.ArgumentParser(description='utanet_scraper.pyで抽出した曲情報から特定の項目を抽出')
    parser.add_argument('input', type=str, help='入力ファイル名')
    parser.add_argument('output', type=str, help='出力ファイル名')
    parser.add_argument('-a', '--attribute', type=str, default='lyric', choices=['title', 'artist', 'lyricist', 'composer', 'lyric'], help="抽出したい項目（デフォルト：'lyric'）")
    parser.add_argument('--allow_dups', action='store_true', help='項目の重複を許容（デフォルト：false）')
    parser.add_argument('--sort', action='store_true', help='項目をソートして保存（デフォルト：false）')
    args = parser.parse_args()

    with Path(args.input).open(encoding='utf-8') as input:
        results = json.load(input)

    values = [normalize(result[args.attribute]) for result in results.values()]

    if not args.allow_dups:
        values = set(values)
    if args.sort:
        values = sorted(values)

    with Path(args.output).open('w', encoding='utf-8') as out:
        out.write('\n'.join(values))

if __name__ == "__main__":
    main()
