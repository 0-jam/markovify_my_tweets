#!/bin/bash

### 初期設定
# ディレクトリ名
indir="text"
outdir="text/generated"
# 文章を生成する回数
number=1
# 一度に生成するプロセス数
jobs=1

### スクリプトの使い方を表示し，スクリプトを終了する
usage(){
  cat <<EOS
使用法：bash run.sh [オプション]
markovify_sentence.pyを複数ファイルに対して一括で実行する

  -i [NAME]    学習対象のファイルが存在するディレクトリ名を指定（デフォルト：text）
  -o [NAME]    結果ファイルの出力先ディレクトリ名を指定（デフォルト：text/generated）
  -j [VALUE]   markovify_sentence.pyが一度に生成するプロセス数を指定（デフォルト：1）
  -n [VALUE]   テキスト生成を実行する回数を指定（デフォルト：1）
  -h           このヘルプを表示して終了
EOS
  exit 1
}

### オプションの処理
while getopts "hi:n:o:j:" opts; do
  case $opts in
    h|\?)
      usage
      ;;
    i)
      indir=$OPTARG
      ;;
    o)
      outdir=$OPTARG
      ;;
    j)
      jobs=$OPTARG
      ;;
    n)
      number=$OPTARG
      ;;
  esac
done

if [ ! -d $outdir ]; then
  echo "mkdir -p $outdir"
  mkdir -p ${outdir}
fi

while read -r f; do
  # $ findで抽出したファイル名からディレクトリ名と拡張子を除去
  # その後ろに"_markovified.txt"を追加して出力ファイル名とする
  echo "markovify_sentence.py $f -o ${outdir%/}/$(basename ${f%.*})_markovified.txt -n ${number} -j ${jobs}"
  python markovify_sentence.py $f -o ${outdir%/}/$(basename ${f%.*})_markovified.txt -n ${number} -j ${jobs}
done < <(find ${indir} -maxdepth 1 -type f -name "*.txt")
