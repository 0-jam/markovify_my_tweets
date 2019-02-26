import argparse
from pathlib import Path
from tqdm import tqdm
import unicodedata
from modules.multi_sub import replace_str

## Divide text by word using specified engine
def main():
    parser = argparse.ArgumentParser(description='Preprocessing script for Japanese text.')
    parser.add_argument('input', type=str, help='Input file path')
    parser.add_argument('output', type=str, help='Output file path')
    parser.add_argument('-e', '--engine', type=str, default='mecab', choices=['janome', 'mecab', 'juman'], help='Tokenize engine (default: mecab)')
    parser.add_argument('-r', '--allow_empty', action='store_true', help="Don't remove empty line")
    parser.add_argument('--encoding', type=str, default='utf-8', help='Encoding of target text file (default: utf-8)')
    args = parser.parse_args()

    # Select engine for word dividing
    if args.engine in {'janome'}:
        from modules.wakachi.janome import divide_word
    elif args.engine in {'mecab'}:
        from modules.wakachi.mecab import divide_word
    elif args.engine in {'juman'}:
        from modules.wakachi.juman import divide_word

    input_path = Path(args.input)
    with input_path.open(encoding=args.encoding) as input, Path(args.output).open('w', encoding='utf-8') as out:
        with tqdm(total=input_path.stat().st_size, unit='kb', unit_scale=0.001, smoothing=1) as pbar:
            patterns = [(r'\.{3,}', '…'), (r'・{3,}', '…'), (r'…{2,}', '…')]
            for line in input:
                line = unicodedata.normalize('NFKC', line.strip())
                line = replace_str(line, patterns)

                if not (line or args.allow_empty):
                    continue

                out.write(' '.join(divide_word(line)) + '\n')
                pbar.update(len(line.encode('utf-8')))

if __name__ == '__main__':
    main()
