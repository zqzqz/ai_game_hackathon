#!/bin/sh
for f in ./*.py; do
	tr -d '\r' < $f > new.py
	rm $f
	mv new.py $f
done

chmod +x main.py
