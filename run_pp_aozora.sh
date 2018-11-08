#!/bin/bash

### Initialize
# Input / output file location
indir="text/novel_orig"
outdir="text/novel"
# Enable word divider
wakachi=""
# Postfix of the file name
postfix="noruby"

usage(){
  cat <<EOS
Usage: bash run_pp_aozora.sh [OPTIONS]
Execute pp_aozora.py to multiple files at once

  -i [NAME]    Path to file to convert (directory) (default: ./text/novel_orig)
  -o [NAME]    Path to output file (directory) (default: ./text/novel)
  -e [NAME]    Enable word divider using specified engine
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
