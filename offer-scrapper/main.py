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
import os
import re
import pickle

from args import Args

page=1
URL="http://jobs-stages.letudiant.fr/stages-etudiants/offres/domaines-103_129_165_111/niveaux-3_2_9/page-" + str(page) + ".html"
result_file="/home/marrakchino/github/letudiant-offers-scrapper/.results.txt"
tmp_result_file="/home/marrakchino/github/letudiant-offers-scrapper/.results.txt.tmp"
args = Args()

class Colors:
    HEADER = '\033[95m'
    DARKBLUE = '\033[34m'
    BLUE = '\033[94m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class Offer:
    def __init__(self, company, title, location, description = None):
        self.company = company
        self.title = title
        self.location = location
        if (description != None):
            self.description = description
        else:
            self.description = ""

    def __str__(self):
        return self.company + '({}): {}'.format(self.location, self.description)

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
        if len(elt.company) > max_company_name_len:
            max_company_name_len = len(elt.company)
        if len(elt.title) > max_offer_title_len:
            max_offer_title_len = len(elt.title)

    if filter == None:
        for offer in range(len(offers_list)):
            if offer % 10 == 0:
                print(Colors.DARKBLUE + "Page " + str(offer / 10 + 1))

            print(Colors.HEADER + "[" + str(offer) + "]" + 
            offers_list[offer].company + 
            " " * (max_company_name_len - len(offers_list[offer].company))+ 
            Colors.ENDC + Colors.GREEN + offers_list[offer].title + 
            " " * (max_offer_title_len - len(offers_list[offer].title))+ 
            Colors.BLUE + offers_list[offer].location + Colors.ENDC)

    else:
        for offer in range(len(offers_list)):
            title = offers_list[offer].title.lower().split()
            company = offers_list[offer].company.lower().split()
            location = offers_list[offer].location.lower().split()
            for f in filter:
                if offer % 10 == 0:
                    print(Colors.DARKBLUE + "Page " + str(offer / 10 + 1))
                f = f.lower()
                if f in title or f in company or f in location:
                    # TODO: use 're' to highlight the found filter keyword (in title, company name, or location)
                    print(Colors.HEADER + "[" + str(offer) + "]" + 
                    offers_list[offer].company + 
                    " " * (max_company_name_len - len(offers_list[offer].company))+ 
                    Colors.ENDC + Colors.GREEN + offers_list[offer].title + 
                    " " * (max_offer_title_len - len(offers_list[offer].title))+ 
                    Colors.BLUE + offers_list[offer].location + Colors.ENDC)


def next_page():
    global URL
    global page
    URL=URL.replace("page-" + str(page), "page-" + str(page+1))
    page += 1

def parse_pages(n, filter=[], new=False, interactive=False):
    global page
    global URL

    offer_url_list=[]
    offers = [] # list of offers

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

            offers.append(Offer(company, title, location))

        next_page()

    dump_content(offers, tmp_result_file)
    display_results(new, filter)

    if interactive:
        def select_offer(query):
            offer_url=re.sub(r"\/stages-etudiants.*", offer_url_list[int(query)], URL)
            r_offer=urllib.urlopen(offer_url)
            r_soup=BeautifulSoup(r_offer, "lxml")
            
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
