#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: marrakchino

from bs4 import BeautifulSoup
import urllib
import sys

from utils import Colors
from args import Args

pages=int(sys.argv[1])
if pages >= 50:
    print("Max page number: 49")
    exit(1)

p=1
i = 0
URL="http://jobs-stages.letudiant.fr/stages-etudiants/offres/domaines-103_129_165/niveaux-3_2_9/page-" + str(p) + ".html"
while p <= pages:
    r=urllib.urlopen(URL)
    soup=BeautifulSoup(r)
    offer_titles=soup.find_all("a", class_="c-search-result__title")
    offer_companies=soup.find_all("span", class_="  ")
    offer_location=soup.find_all("span", class_="  u-typo-italic ")
    if len(offer_titles) != len(offer_companies):
        print("The number of offers doesn't correspond to the number of companies")
        exit(1)

    while i < p * len(offer_titles):

        title=offer_titles[i / p].text
        company=offer_companies[i / p ].text
        location=offer_location[i / p ].text

        # silence 'not-so-exciting' offers' locations
        if len(location) > 25:
            location=location.split(",", 1)[0] + " ..."
        # no need for the publication date
        if title.find("Publi") != -1:
            title=title[:title.find("Publi") - 1]
        
        print(Colors.GREEN + "[" + str(i) + "]" + Colors.YELLOW + company + Colors.ENDC + Colors.GREEN + title + Colors.BLUE + location + Colors.ENDC)
        i += 1

    URL=URL.replace("page-" + str(p), "page-" + str(p+1))
    p += 1

