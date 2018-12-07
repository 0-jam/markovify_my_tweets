#!/bin/bash

### Initialize
# Input / output file location
indir="text/novel_orig"
outdir="text/novel"
# Engine of word divider
engine="mecab"

usage(){
  cat <<EOS
Usage: bash run_wakachi.sh [OPTIONS]
Execute wakachi.py to multiple files at once

  -i [NAME]    Path to file to convert (directory) (default: ./text/novel_orig)
  -o [NAME]    Path to output file (directory) (default: ./text/novel)
  -e [NAME]    Specify the engine of word divider (default: MeCab)
  -h           Print this help
EOS
  exit 1
}

### Parse options
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
      engine=$OPTARG
      ;;
  esac
done

if [ ! -d $outdir ]; then
  echo "mkdir -p $outdir"
  mkdir -p ${outdir}
fi

while read -r f; do
  echo "wakachi.py $f ${outdir%/}/$(basename ${f%.*})_wakachi.txt -e ${engine}"
  python wakachi.py $f ${outdir%/}/$(basename ${f%.*})_wakachi.txt -e ${engine}
done < <(find ${indir} -maxdepth 1 -type f -name "*.txt")
