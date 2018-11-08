#!/bin/bash

### Initialize
# Input / output file location
indir="text"
outdir="text/generated"
# Number of text to generate
number=1
# Number of processes
jobs=1

usage(){
  cat <<EOS
Usage: bash run_markovify.sh [OPTIONS]
Execute markovify_sentence.py to multiple files at once

  -i [NAME]    Path of training dataset (directory) （default: ./text)
  -o [NAME]    Path of generated text (directory) (default: ./text/generated)
  -j [VALUE]   Number of processes (default: 1)
  -n [VALUE]   Number of text to generate (default: 1)
  -h           Print this help
EOS
  exit 1
}

### Parse options
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
  # Remove directory name and extention from the file name
  # Append "_markovified.txt" to the original file name
  echo "markovify_sentence.py $f -o ${outdir%/}/$(basename ${f%.*})_markovified.txt -n ${number} -j ${jobs}"
  python markovify_sentence.py $f -o ${outdir%/}/$(basename ${f%.*})_markovified.txt -n ${number} -j ${jobs}
done < <(find ${indir} -maxdepth 1 -type f -name "*.txt")
