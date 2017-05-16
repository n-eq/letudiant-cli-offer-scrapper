#!/bin/sh -e

for i in `seq 1 5`; do
	echo "python offer-scrapper/main.py --pages $i ..."
	python offer-scrapper/main.py --pages "$i"
done

for filter in C Paris Web; do
	echo "python offer-scrapper/main.py --filter $filter ..."
	python offer-scrapper/main.py --filter "$filter"
done

echo "Done, so far so good."
