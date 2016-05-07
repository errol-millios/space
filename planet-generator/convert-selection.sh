#!/bin/bash

for f in selection/*.bmp; do
    file=${f##*/}
    name=${file%.*}
    outfile=selection/"$name".jpg
    if [ ! -e "$outfile" ]; then
	echo "$f" '->' "$outfile"
	convert "$f" "$outfile"
    fi
done
