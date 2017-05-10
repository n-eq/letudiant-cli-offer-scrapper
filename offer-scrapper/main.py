#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import urllib
import sys, os
import subprocess as sp
import difflib
import shutil
import re
import random

from utils import Colors
from args import Args

p=1
URL="http://jobs-stages.letudiant.fr/stages-etudiants/offres/domaines-103_129_165_111/niveaux-3_2_9/page-" + str(p) + ".html"
result_file="../.results.txt"
args = Args()

def next_page():
    global URL
    global p
    URL=URL.replace("page-" + str(p), "page-" + str(p+1))
    p += 1

if args.number_of_pages != None and args.number_of_days != None:
    print("You can only specify a number of pages or a number of days, incompatible arguments.")
    exit(1)

def parse_pages(n, filter=[], new=False, interactive=False):
    f=os.open(result_file, os.O_RDWR|os.O_CREAT|os.O_APPEND)
    new_f=os.open(result_file + ".tmp", os.O_RDWR|os.O_CREAT)
    sp.call('clear', shell=True)
    print(vars(args)) #DEBUG
    global p
    global URL
    i = 0
    offer_url_list=[]
    while p <= n:
        r=urllib.urlopen(URL)
        soup=BeautifulSoup(r)

        offer_titles=soup.find_all("a", class_="c-search-result__title")
        offer_url_list.extend([offer_titles[j]['href'] for j in range(len(offer_titles))])
        offer_companies=soup.find_all("span", class_="  ")
        offer_locations=soup.find_all("span", class_="  u-typo-italic ")
        
        if len(offer_titles) != len(offer_companies):
            print("The number of offers doesn't correspond to the number of companies")
            exit(1)

        print(Colors.HEADER + "Page " + str(p))
        while i < p * len(offer_titles):
            title=offer_titles[i / p].text
            company=offer_companies[i / p].text
            location=offer_locations[i / p].text

            # silence 'not-so-exciting' offers' locations
            if len(location) > 25:
                location=location.split(",", 1)[0] + " ..."
            # no need for the publication date
            if title.find("Publi") != -1:
                title=title[:title.find("Publi") - 1]

            tmp_result=Colors.GREEN + "[" + str(i) + "]" + Colors.BOLD + company + Colors.ENDC + Colors.GREEN + title + Colors.BLUE + location + Colors.ENDC

            def write_results():
                os.write(os.open(result_file + ".tmp", os.O_RDWR|os.O_APPEND|os.O_CREAT), (tmp_result + "\n").encode('utf-8'))
#                 if not new:
#                     print(tmp_result)

            def show_results():
                if new:
                    # TODO: not working
                    diff=difflib.ndiff(os.read(os.open(result_file + ".tmp", os.O_RDWR|os.O_APPEND|os.O_CREAT), 10), os.read(f, 10))
                    print ''.join(diff)
                            
                else:
                    os.rename(result_file + ".tmp", result_file)
                    sp.call("cat " + result_file, shell=True)
            
            if filter != None:
                for f in filter:
                    if f in title:    
                        write_results()
            else:
                write_results()

            i += 1
            show_results()

        next_page()

    if interactive:
        def select_offer(query):
            # TODO: find a better way to extract the url (maybe replace a pattern!)
            offer_url=URL[:31] + offer_url_list[int(query)]
            r_offer=urllib.urlopen(offer_url)
            r_soup=BeautifulSoup(r_offer)
            paragraphs=r_soup.find_all('h5', text=False)

            print("=" * 150)
            for l in range(len(r_soup.find_all('p'))):
                print(Colors.YELLOW + (r_soup.find_all('p')[l].text) + Colors.ENDC)
            print("=" * 150)

            
        while (True):
            query=raw_input(Colors.UNDERLINE + "Enter your query (q to quit):" + Colors.ENDC + " ")
            if (query == "q"):
                break
            else:
                if (int(query) < 10 * n):
                    select_offer(query)
                else:
                    print("Wrong number, try again.")


def parse_days(n, filter=[]):
    print("Not yet implemented")

def parse_new():
    print("Not yet implemented")


def parse_company(company_name):
    print("Not yet implemented")

def main():
    if args.number_of_pages:
        parse_pages(args.number_of_pages, args.filter_search, args.new, args.interactive_mode)

    elif args.number_of_days:
        parse_days(args.number_of_days, args.filter_search)

    else: # Default
        parse_pages(args.number_of_pages, args.filter_search, args.new, args.interactive_mode)

if __name__ == "__main__":
    main()
