#!/bin/bash

### 初期設定
# ディレクトリ名
indir="text/novel_orig"
outdir="text/novel"
wakachi=""
postfix="noruby"

### スクリプトの使い方を表示し，スクリプトを終了する
usage(){
  cat <<EOS
使用法：bash run.sh [オプション]
pp_aozora.pyを複数ファイルに対して一括で実行する

  -i [NAME]    学習対象のファイルが存在するディレクトリ名を指定（デフォルト：text/novel_orig）
  -o [NAME]    結果ファイルの出力先ディレクトリ名を指定（デフォルト：text/novel）
  -e [NAME]    指定したエンジン名で分かち書きを有効にする
  -h           このヘルプを表示して終了
EOS
  exit 1
}

### オプションの処理
while getopts "he:i:o:" opts; do
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
    e)
      wakachi=" -e ${OPTARG}"
      postfix="wakachi"
      ;;
  esac
done

if [ ! -d $outdir ]; then
  echo "mkdir -p $outdir"
  mkdir -p ${outdir}
fi

while read -r f; do
  echo "pp_aozora.py $f ${outdir%/}/$(basename ${f%.*})_${postfix}.txt${wakachi}"
  python pp_aozora.py $f ${outdir}/$(basename ${f%.*})_${postfix}.txt${wakachi}
done < <(find ${indir} -maxdepth 1 -type f -name "*.txt")
