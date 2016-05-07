all: wg wg-cgi

wg: worldgen-2.2a.c
	gcc -O3 worldgen-2.2a.c -lm -o wg
wg-cgi: WorldMapGenerator.c
	gcc -O3 WorldMapGenerator.c -lm -o wg-cgi
