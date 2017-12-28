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
import time

from args import Args

page = 1
URL = "http://jobs-stages.letudiant.fr/stages-etudiants/offres/domaines-103_129_165_111/niveaux-9_1/page-" + str(page) + ".html"
result_file = "/home/marrakchino/github/letudiant-offers-scrapper/.results.txt"
tmp_result_file = "/home/marrakchino/github/letudiant-offers-scrapper/.results.txt.tmp"

class Colors:
    HEADER = '\033[95m'
    DARKBLUE = '\033[34m'
    BLUE = '\033[94m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class Offer:
    def __init__(self, company, title, location, date = None, description = None):
        self.company = company
        self.title = title
        self.location = location
        if (date != None):
            self.date = date
        else:
            self.date = "01/01/1970"
        if (description != None):
            self.description = description
        else:
            self.description = ""

    def __repr__(self):
        return self.company + ' ({}, {}): {} - {}'.format(self.location, self.date, self.title, self.title, self.description)

    def __str__(self):
        return self.company + ' ({}, {}): {} - {}'.format(self.location, self.date, self.title, self.title, self.description)

def replace_accents(s):
    replacements = {u"é": "e", u"è": "e", u"ê": "e", u"à": "a", u"â": "a", u"î": "i", u"û": "u", u"ô": "o"}
    for c in replacements.keys():
        s.replace(c, replacements[c])
    return s

def dump_content(offers_to_dump, destination):
    pickle.dump(offers_to_dump, open(destination, "wb"))

def display_results(new, filter):
    if new:
        previous_content = pickle.load(open(result_file, "rb"))
        fresh_content = pickle.load(open(tmp_result_file, "rb"))
        offers_list=[]
        for offer in fresh_content:
            if offer not in previous_content:
                offers_list.append(offer)
    else:
        offers_list = pickle.load(open(tmp_result_file, "rb"))
        os.rename(tmp_result_file, result_file)

    max_company_name_len = max([len(offer.company) for offer in offers_list])
    max_offer_title_len = max([len(offer.title) for offer in offers_list])

    if filter == None:
        for offer in range(len(offers_list)):
            if offer == 0:
                print(Colors.DARKBLUE + "Page 1")
            if offer % 10 == 7:
                print(Colors.DARKBLUE + "Page " + str(offer / 10 + 2))

            print(Colors.HEADER + "[" + str(offer) + "]" + (" " if (len(offers_list) > 10 and offer < 10) else "") + offers_list[offer].company + 
            " " * (max_company_name_len - len(offers_list[offer].company))+ 
            Colors.ENDC + Colors.GREEN + offers_list[offer].title + 
            " " * (max_offer_title_len - len(offers_list[offer].title))+ 
            Colors.BLUE + offers_list[offer].location + Colors.ENDC).encode("utf-8")

    else:
        for offer in range(len(offers_list)):
            title = offers_list[offer].title.lower().split()
            company = offers_list[offer].company.lower().split()
            location = offers_list[offer].location.lower().split()
            for f in filter:
                if offer == 0:
                    print(Colors.DARKBLUE + "Page 1")
                if offer % 10 == 7:
                    print(Colors.DARKBLUE + "Page " + str(offer / 10 + 2))

                f = f.lower()

                if f in title or f in company or f in location:
                    # TODO: use 're' to highlight the found filter keyword (in title, company name, or location)
                    print(Colors.HEADER + "[" + str(offer) + "]" + 
                    (" " if (len(offers_list) > 10 and offer < 10) else "") +
                    offers_list[offer].company + 
                    " " * (max_company_name_len - len(offers_list[offer].company))+ 
                    Colors.ENDC + Colors.GREEN + offers_list[offer].title + 
                    " " * (max_offer_title_len - len(offers_list[offer].title))+ 
                    Colors.BLUE + offers_list[offer].location + Colors.ENDC).encode("utf-8")


def next_page():
    global URL
    global page
    URL = URL.replace("page-" + str(page), "page-" + str(page+1))
    page += 1

def parse_pages(n, filter = [], new = False, interactive = False):
    global page
    global URL

    offer_url_list = []
    offers = [] # list of offers

    while page <= n:
        r = urllib.urlopen(URL)
        soup = BeautifulSoup(r, 'lxml')

        # extract information using tags and class names
        offer_titles = soup.find_all("a", class_ = "c-search-result__title")
        offer_url_list.extend([offer_titles[j]['href'] for j in range(len(offer_titles))])
        offer_companies = soup.find_all("span", class_ = " ")
        offer_locations = soup.find_all("span", class_ = " u-typo-italic ")
        
        if len(offer_titles) != len(offer_companies):
            print("The number of offers (" + str(len(offer_titles)) + ") doesn't correspond to the number of companies (" + str(len(offer_companies)) + ")")
            exit(1)

        # loop over found offers
        k = 0
        if page == 1:
            k = 3
        while k < len(offer_titles):
            title = offer_titles[k].text
            company = offer_companies[k].text
            location = offer_locations[k].text
            k += 1

            # no need for the publication date
            if title.find("Publi") != -1:
                title = title[:title.find("Publi") - 1]

            offers.append(Offer(replace_accents(company),
                                replace_accents(title),
                                replace_accents(location)))

        next_page()

    dump_content(offers, tmp_result_file)
    display_results(new, filter)

    if interactive:
        def select_offer(query):
            offer_url = re.sub(r"\/stages-etudiants.*", offer_url_list[int(query)], URL)
            r_offer = urllib.urlopen(offer_url)
            r_soup=BeautifulSoup(r_offer, "lxml")
            
            print("=" * 150)
            for l in range(len(r_soup.find_all('p'))):
                print(Colors.YELLOW + (r_soup.find_all('p')[l].text) + Colors.ENDC)
            print("=" * 150)

            
        while (True):
            query = raw_input(Colors.UNDERLINE + "Enter your query (q to quit):" + Colors.ENDC + " ")
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


def parse_days(n, filter = [], interactive = False):
    global page
    global URL
    offer_url_list = []

    from datetime import datetime, date, timedelta
    from dateutil import parser

    today = datetime.today()
    margin = timedelta(days = n)
    offers = []
    enough = False # trick to exit the two nested loops...

    while True:
        r=urllib.urlopen(URL)
        soup=BeautifulSoup(r, 'lxml')

        offer_titles = soup.find_all("a", class_ = "c-search-result__title")
        offer_url_list.extend([offer_titles[j]['href'] for j in range(len(offer_titles))])
        offer_companies = soup.find_all("span", class_ = " ")
        offer_locations = soup.find_all("span", class_ = " u-typo-italic ")

        offer_dates = soup.find_all("span", class_ = "c-search-result__title__date")
        parsed_dates = [parser.parse(date.text[re.search("\d", date.text).start():].replace(' ', '')) for date in offer_dates]

        j = 0; k = 0
        if page == 1:
            k = 3
        while k < len(offer_titles):
            title = offer_titles[k].text
            company = offer_companies[k].text
            location = offer_locations[k].text
            date = parsed_dates[j] 

            if title.find("Publi") != -1:
                title = title[:title.find("Publi") - 1]

            if date >= today - margin and date <= today:
                offers.append(Offer(replace_accents(company),
                                    replace_accents(title),
                                    replace_accents(location),
                                    str(date)))
            else:
                enough = True
                break
            k += 1
            j += 1

        next_page()
        if enough:
            break

    max_company_name_len = max([len(offer.company) for offer in offers])
    max_offer_title_len = max([len(offer.title) for offer in offers])

    if filter == None:
        for offer in range(len(offers)):
            print(Colors.HEADER + "[" + str(offer) + "]" + 
            offers[offer].company + 
            " " * (max_company_name_len - len(offers[offer].company))+ 
            Colors.ENDC + Colors.GREEN + offers[offer].title + 
            " " * (max_offer_title_len - len(offers[offer].title))+ 
            Colors.BLUE + offers[offer].location + Colors.ENDC).encode("utf-8")

#     else:
    

def parse_company(company_name):
    print("Not yet implemented")

def main():
    args = Args()
    if args.number_of_days:
        parse_days(args.number_of_days, args.filter_search, args.interactive_mode)

    else: # Default
        parse_pages(args.number_of_pages, args.filter_search, args.new, args.interactive_mode)

if __name__ == "__main__":
    main()
