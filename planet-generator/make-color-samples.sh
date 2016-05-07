#!/bin/bash

set -e

for f in source-images/*; do
    file=${f##*/}
    name=${file%.*}
    outfile=small-images/"$name".png
    if [ ! -e "$outfile" ]; then
	python make-small.py "$f" "$outfile"
    fi
done

for f in small-images/*; do
    file=${f##*/}
    name=${file%.*}
    outfile=colors/"$name".col
    if [ ! -e "$outfile" ]; then
	python image-histogram.py "$f" > "$outfile"
    fi
done

for n in $(seq 20); do
    seed=$(printf '%03d\n' $n)
    for col in colors/*; do
	file=${col##*/}
	name=${file%.*}
	outfile=output-images/"$name".$seed.bmp
	if [ ! -e "$outfile" ]; then
	    ./planet -C $col -w 200 -h 200 -p o -s 0.$seed > "$outfile"
	fi
    done
done

exit

for f in output-images/*; do
    file=${f##*/}
    name=${file%.*}
    outfile=final-images/"$name".png
    if [ ! -e "$outfile" ]; then
	python make-transparent.py "$f" "$outfile"
    fi
done
