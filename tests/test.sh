#!/bin/bash -e

WHITE='\033[1;37m'
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# test (multi)page parsing
for i in $(seq 1 10); do
	printf "${WHITE}python offer-scrapper/main.py --pages $i ..."
	python offer-scrapper/main.py --pages "$i" >> tests/tmp_$$
    # check that we have the correct numberof lines  (10 (offers/page) + 1) per page requested
    # .. and check also that the lines are unique (no duplicates as in previous issues)
    if [[ $(uniq tests/tmp_$$| wc -l| cut -d' ' -f1) -ne  $((i * 11)) ]]; then
        printf "${RED} failed${NC}\n"
        rm -f tests/tmp_$$
        exit
    else
        printf "${GREEN} OK${NC}\n"
    fi
    rm -f tests/tmp_$$
done

