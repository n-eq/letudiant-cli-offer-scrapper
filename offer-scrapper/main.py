#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: marrakchino

from bs4 import BeautifulSoup
import urllib
import sys

from utils import Colors
from args import Args

p=1
URL="http://jobs-stages.letudiant.fr/stages-etudiants/offres/domaines-103_129_165/niveaux-3_2_9/page-" + str(p) + ".html"
args = Args()
# print(vars(args))

def next_page():
    global URL
    global p
    URL=URL.replace("page-" + str(p), "page-" + str(p+1))
    p += 1

if args.number_of_pages != None and args.number_of_days != None:
    print("You can only specify a number of pages or a number of days, incompatible arguments.")
    exit(1)

def parse_pages(n, filter=[]):
    global p
    global URL
    i = 0
    while p <= n:
        r=urllib.urlopen(URL)
        soup=BeautifulSoup(r)
        offer_titles=soup.find_all("a", class_="c-search-result__title")
        offer_companies=soup.find_all("span", class_="  ")
        offer_location=soup.find_all("span", class_="  u-typo-italic ")
        if len(offer_titles) != len(offer_companies):
            print("The number of offers doesn't correspond to the number of companies")
            exit(1)

        print(Colors.HEADER + "Page " + str(p))
        while i < p * len(offer_titles):
            title=offer_titles[i / p].text
            company=offer_companies[i / p].text
            location=offer_location[i / p].text

            # silence 'not-so-exciting' offers' locations
            if len(location) > 25:
                location=location.split(",", 1)[0] + " ..."
            # no need for the publication date
            if title.find("Publi") != -1:
                title=title[:title.find("Publi") - 1]
            
            if len(filter) > 0:
                for f in filter:
                    if f in title:
                        print(Colors.GREEN + "[" + str(i) + "]" + Colors.BOLD + company + Colors.ENDC + Colors.GREEN + title + Colors.BLUE + location + Colors.ENDC)
            else:
                print(Colors.GREEN + "[" + str(i) + "]" + Colors.BOLD + company + Colors.ENDC + Colors.GREEN + title + Colors.BLUE + location + Colors.ENDC)

            i += 1

        next_page()

def parse_days(n, filter=[]):
    print("Not yet implemented")

def parse_new():
    print("Not yet implemented")


def parse_company(company_name):
    print("Not yet implemented")

def main():
#     print(vars(args)) #DEBUG
    if args.number_of_pages:
        if args.filter_search:
            parse_pages(args.number_of_pages, args.filter_search)
        else:
            parse_pages(args.number_of_pages)
    elif args.number_of_days:
        if args.filter_search:
            parse_days(args.number_of_days, args.filter_search)
        else:
            parse_days(args.number_of_days)

    else: # Default
        parse_pages(1)

if __name__ == "__main__":
    main()
