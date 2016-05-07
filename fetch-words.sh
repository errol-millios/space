#!/bin/bash
>/tmp/english3000.txt
for url in http://www.paulnoll.com/Books/Clear-English/words-01-02-hundred.html \
	   http://www.paulnoll.com/Books/Clear-English/words-03-04-hundred.html \
	   http://www.paulnoll.com/Books/Clear-English/words-05-06-hundred.html \
	   http://www.paulnoll.com/Books/Clear-English/words-07-08-hundred.html \
	   http://www.paulnoll.com/Books/Clear-English/words-09-10-hundred.html \
	   http://www.paulnoll.com/Books/Clear-English/words-11-12-hundred.html \
	   http://www.paulnoll.com/Books/Clear-English/words-13-14-hundred.html \
	   http://www.paulnoll.com/Books/Clear-English/words-15-16-hundred.html \
	   http://www.paulnoll.com/Books/Clear-English/words-17-18-hundred.html \
	   http://www.paulnoll.com/Books/Clear-English/words-19-20-hundred.html \
	   http://www.paulnoll.com/Books/Clear-English/words-21-22-hundred.html \
	   http://www.paulnoll.com/Books/Clear-English/words-23-24-hundred.html \
	   http://www.paulnoll.com/Books/Clear-English/words-25-26-hundred.html \
	   http://www.paulnoll.com/Books/Clear-English/words-27-28-hundred.html \
	   http://www.paulnoll.com/Books/Clear-English/words-29-30-hundred.html; do

    curl -s $url | dos2unix | sed -e 's/>/>\n/g' -e 's/</\n</' | sed -n '/.*<ol.*/,/<td colspan/ p' | sed -r -e 's/^[ \t]+//' -e '/^</d' | tr '[:upper:]' '[:lower:]' | sort -u > /tmp/words
    echo $? $url $(wc -l < /tmp/words)
    cat /tmp/words >> /tmp/english3000.txt
done

grep -v ^$ < /tmp/english3000.txt | grep -v -P "[^a-zA-Z]" | sort -u > english3000.txt
