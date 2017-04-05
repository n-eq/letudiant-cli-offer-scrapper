#!/usr/bin/python
# -*- coding: utf-8 -*-

# -d 0 pour offres d'auj, -d 1 hier ... -n, new
from bs4 import BeautifulSoup
import urllib
import sys

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[34m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

URL="http://jobs-stages.letudiant.fr/stages-etudiants/offres/domaines-103_129_165/niveaux-3_2_9/page-1.html"

r=urllib.urlopen(URL)
soup=BeautifulSoup(r)

offer_titles=soup.find_all("a", class_="c-search-result__title")
offer_companies=soup.find_all("span", class_="  ")
offer_location=soup.find_all("span", class_="  u-typo-italic ")

if len(offer_titles) != len(offer_companies):
    print("The number of offers doesn't correspond to the number of companies")
    exit(1)

i = 0
while i < len(offer_titles):
    title=offer_titles[i].text
    company=offer_companies[i].text
    location=offer_location[i].text

    # silence 'not-so-exciting' offers' locations
    if len(location) > 25:
        location=location.split(",", 1)[0] + " ..."
    # no need for the publication date
    if title.find("Publi") != -1:
        title=title[:title.find("Publi") - 1]
    
    print(bcolors.OKGREEN + "[" + str(i) + "]" + bcolors.WARNING + company + bcolors.ENDC + bcolors.OKGREEN + title + bcolors.OKBLUE + location + bcolors.ENDC)
    i += 1
