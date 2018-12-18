#!/bin/bash

### Initialize
# Input / output file location
indir="text/novel_orig"
outdir="text/novel"
# Postfix of the file name
postfix="noruby"

usage(){
  cat <<EOS
Usage: bash run_pp_aozora.sh [OPTIONS]
Execute pp_aozora.py to multiple files at once

  -i [NAME]    Path to file to convert (directory) (default: ./text/novel_orig)
  -o [NAME]    Path to output file (directory) (default: ./text/novel)
  -h           Print this help
EOS
  exit 1
}

### Parse options
while getopts "hi:o:" opts; do
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
  esac
done

if [ ! -d $outdir ]; then
  echo "mkdir -p $outdir"
  mkdir -p ${outdir}
fi

while read -r f; do
  echo "pp_aozora.py $f ${outdir%/}/$(basename ${f%.*})_${postfix}.txt"
  python pp_aozora.py $f ${outdir}/$(basename ${f%.*})_${postfix}.txt
done < <(find ${indir} -maxdepth 1 -type f -name "*.txt")
