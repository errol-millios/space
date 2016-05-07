#!/bin/bash


for n in $(seq 100); do
    seed=$(printf '%03d\n' $n)
    ./planet -C Olsson.col -w 64 -h 64 -p o -s 0.$seed > tests/test-$seed.bmp

done
