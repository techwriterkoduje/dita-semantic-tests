#!/bin/bash

SRC_IMG_DIR=$1
SRC_FORMAT=$2
OUT_FORMAT=$3
OUT_DIR=out

mkdir -p $OUT_DIR
for filePath in "$SRC_IMG_DIR"/*."$SRC_FORMAT"; do
  filePathBasename=$(basename -s ".${SRC_FORMAT}" "$filePath")
  outFilePath="$OUT_DIR"/"$filePathBasename"."$OUT_FORMAT"
  echo Converting "$filePath" to "$outFilePath"
  cp "$filePath" "$outFilePath"
done