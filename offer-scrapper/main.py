#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
letudiant.fr Command-line interface offer scrapper

Copyright (c) 2017 Nabil Elqatib (nabilelqatib@gmail.com)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from bs4 import BeautifulSoup
import urllib
import sys, os
import re
import pickle

from args import Args

page=1
URL="http://jobs-stages.letudiant.fr/stages-etudiants/offres/domaines-103_129_165_111/niveaux-3_2_9/page-" + str(page) + ".html"
result_file="/home/marrakchino/github/letudiant-offers-scrapper/.results.txt"
tmp_result_file="/home/marrakchino/github/letudiant-offers-scrapper/.results.txt.tmp"
args = Args()

if args.number_of_pages != None and args.number_of_days != None:
    print("You can either specify a number of pages or a number of days, incompatible arguments.")
    exit(1)


class Colors():
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def replace_accents(s):
    replacements = {u"é": "e", u"è": "e", u"ê": "e", u"à": "a", u"â": "a", u"î": "i", u"û": "u", u"ô": "o"}
    for c in replacements.keys():
        s.replace(c, replacements[c])
    return s

def dump_content(offers_to_dump, destination):
    pickle.dump(offers_to_dump, open(destination, "wb"))

def display_results(new, filter):
    results_to_show=[]
    if new:
        previous_content = pickle.load(open(result_file, "rb"))
        fresh_content = pickle.load(open(tmp_result_file, "rb"))
        offers = [off for off in previous_content + fresh_content if (off not in fresh_content) or (off not in previous_content)]
        offers_list = offers
    else:
        dumped_content=pickle.load(open(tmp_result_file, "rb"))
        os.rename(tmp_result_file, result_file)
        offers_list = dumped_content

    max_company_name_len = 0
    max_offer_title_len = 0
    for elt in offers_list:
        if len(elt[0]) > max_company_name_len:
            max_company_name_len = len(elt[0])
        if len(elt[1]) > max_offer_title_len:
            max_offer_title_len = len(elt[1])

    if filter == None:
        for offer in range(len(offers_list)):
            if offer % 10 == 0:
                print(Colors.HEADER + "Page " + str(offer / 10 + 1))

            print(Colors.HEADER + "[" + str(offer) + "]" + Colors.BOLD +
            offers_list[offer][0] + 
            " " * (max_company_name_len - len(offers_list[offer][0]))+ 
            Colors.ENDC + Colors.GREEN + offers_list[offer][1] + 
            " " * (max_offer_title_len - len(offers_list[offer][1]))+ 
            Colors.BLUE + offers_list[offer][2] + Colors.ENDC)

    else:
        for offer in range(len(offers_list)):
            for f in filter:
                # grep 'f' in [1] (company name) or [2] (offer title)
                if f.lower() in offers_list[offer][1].lower() or f.lower() in dumped_content[offer][2].lower():
                    if offer % 10 == 0:
                        print(Colors.HEADER + "Page " + str(offer / 10 + 1))

                    print(Colors.HEADER + "[" + str(offer) + "]" + Colors.BOLD +
                    offers_list[offer][0] + 
                    " " * (max_company_name_len - len(offers_list[offer][0]))+ 
                    Colors.ENDC + Colors.GREEN + offers_list[offer][1] + 
                    " " * (max_offer_title_len - len(offers_list[offer][1]))+ 
                    Colors.BLUE + offers_list[offer][2] + Colors.ENDC)

def next_page():
    global URL
    global page
    URL=URL.replace("page-" + str(page), "page-" + str(page+1))
    page += 1

def parse_pages(n, filter=[], new=False, interactive=False):
    global page
    global URL

    offer_i = 0
    offer_url_list=[]
    offers_ready_to_be_dumped=[[] for _ in range(n * 10)]

    while page <= n:
        r=urllib.urlopen(URL)
        soup=BeautifulSoup(r, 'lxml')

        # extract information using tags and class names
        offer_titles=soup.find_all("a", class_="c-search-result__title")
        offer_url_list.extend([offer_titles[j]['href'] for j in range(len(offer_titles))])
        offer_companies=soup.find_all("span", class_=" ")
        offer_locations=soup.find_all("span", class_=" u-typo-italic ")
        
        if len(offer_titles) != len(offer_companies):
            print("The number of offers (" + str(len(offer_titles)) + ") doesn't correspond to the number of companies (" + str(len(offer_companies)) + ")")
            exit(1)

        # loop over found offers
        k=0
        while k < len(offer_titles):
            title=offer_titles[k].text
            company=offer_companies[k].text
            location=offer_locations[k].text
            k+=1

            # silence 'not-so-exciting' offers' locations
            if len(location) > 35:
                location=location.split(",", 1)[0] + " ..."

            # no need for the publication date
            if title.find("Publi") != -1:
                title=title[:title.find("Publi") - 1]

            # offers are appended in their order of display
            offers_ready_to_be_dumped[offer_i].append(replace_accents(company))
            offers_ready_to_be_dumped[offer_i].append(replace_accents(title))
            offers_ready_to_be_dumped[offer_i].append(replace_accents(location))

            offer_i += 1

        next_page()

    dump_content(offers_ready_to_be_dumped[:offer_i], tmp_result_file)
    display_results(new, filter)

    if interactive:
        def select_offer(query):
            offer_url=re.sub(r"\/stages-etudiants.*", offer_url_list[int(query)], URL)
            r_offer=urllib.urlopen(offer_url)
            r_soup=BeautifulSoup(r_offer, "lxml")
            
            # Unused
            # paragraphs=r_soup.find_all('h5', text=False)

            print("=" * 150)
            for l in range(len(r_soup.find_all('p'))):
                print(Colors.YELLOW + (r_soup.find_all('p')[l].text) + Colors.ENDC)
            print("=" * 150)

            
        while (True):
            query=raw_input(Colors.UNDERLINE + "Enter your query (q to quit):" + Colors.ENDC + " ")
            if (query.lower() == "q"):
                break
            else:
                if (int(query) < 10 * n):
                    select_offer(query)
                else:
                    print("Wrong number, try again.")

    # clear temporary file
    if os.path.exists(tmp_result_file):
        os.remove(tmp_result_file)


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
