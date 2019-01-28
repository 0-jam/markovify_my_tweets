import argparse
import json
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Combine JSON in the specified directory")
    parser.add_argument("input", type=str, help="Input directory")
    parser.add_argument("output", type=str, help="Output file name")
    args = parser.parse_args()

    out_data = {}
    for fdic in [json.load(file.open()) for file in Path(args.input).iterdir()]:
        out_data.update(fdic)

    with Path(args.output).open('w', encoding='utf-8') as out:
        out.write(json.dumps(out_data, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
