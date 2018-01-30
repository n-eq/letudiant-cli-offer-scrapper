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

from args import Args

page = 1
URL = "http://jobs-stages.letudiant.fr/stages-etudiants/offres/domaines-103_129_165_111/niveaux-9_1/page-" + str(page) + ".html"

class Colors:
    HEADER = '\033[95m'
    DARKBLUE = '\033[34m'
    BLUE = '\033[94m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Offer:
    def __init__(self, company, title, location, url, date = None, description = None):
        self.company = company
        self.title = title
        self.location = location
        self.url = url
        if (date != None):
            self.date = date
        else:
            self.date = "01/01/1970"
        if (description != None):
            self.description = description
        else:
            self.description = ""

    def __repr__(self):
        return self.company + ' ({}, {}): {} - {}\n{}'.format(self.location, self.date, self.title, self.title, self.description, self.url)

def replace_accents(s):
    replacements = {u"é": "e", u"è": "e", u"ê": "e", u"à": "a", u"â": "a", u"î": "i", u"û": "u", u"ô": "o"}
    for c in replacements.keys():
        s.replace(c, replacements[c])
    return s

def display_offers():
    max_company_name_len = max([len(offer.company) for offer in offers_to_display])
    max_offer_title_len = max([len(offer.title) for offer in offers_to_display])

    for offer in range(len(offers_to_display)):
        if offer == 0:
            print(Colors.DARKBLUE + "Page 1")
        if offer % 10 == 7:
            print(Colors.DARKBLUE + "Page " + str(offer / 10 + 2))

        print(Colors.HEADER + "[" + str(offer) + "]" + (" " if (len(offers_to_display) > 10 and offer < 10) else "") + offers_to_display[offer].company + 
        " " * (max_company_name_len - len(offers_to_display[offer].company))+ 
        Colors.ENDC + Colors.GREEN + offers_to_display[offer].title + 
        " " * (max_offer_title_len - len(offers_to_display[offer].title))+ 
        Colors.BLUE + offers_to_display[offer].location + Colors.ENDC).encode("utf-8")

def next_page():
    global URL
    global page
    URL = URL.replace("page-" + str(page), "page-" + str(page+1))
    page += 1

offers_to_display = []

def parse_pages(n, filter = [], interactive = False):
    global page
    global URL

    offer_url_list = []

    while page <= n:
        try:
            r = urllib.urlopen(URL)
            soup = BeautifulSoup(r, 'lxml')

            # extract information using tags and class names
            offer_titles = soup.find_all("a", class_ = "c-search-result__title")
            offer_companies = soup.find_all("span", class_ = " ")
            offer_locations = soup.find_all("span", class_ = " u-typo-italic ")
            
            # loop over found offers
            k = 0
            if page == 1:
                k = 3
            while k < len(offer_titles):
                url = re.sub(r"\/stages-etudiants.*", offer_titles[k]['href'], URL)
                offer_url_list.append(url)
                title = replace_accents(offer_titles[k].text)
                company = replace_accents(offer_companies[k].text)
                location = replace_accents(offer_locations[k].text)
                k += 1

                # no need for the publication date
                if title.find("Publi") != -1:
                    title = title[:title.find("Publi") - 1]
                
                if filter == None:
                    offers_to_display.append(Offer(company, title, location, url))

                else:
                    append = False
                    for f in filter:
                        f = f.lower().decode('utf-8')
                        if f in title:
                            append = True
                            title = title.replace(f, Colors.BOLD + f + Colors.ENDC + Colors.GREEN)
                        if f in company: 
                            append = True
                            company = company.replace(f, Colors.BOLD + f + Colors.ENDC + Colors.HEADER)
                        if f in location:
                            append = True
                            location = location.replace(f, Colors.BOLD + f + Colors.ENDC + Colors.BLUE)
                        if append:
                            offers_to_display.append(Offer(company, title, location, url))

            next_page()

        except IOError:
            print("There was an error opening \"{}\". " +
            "Please check your internet connection and try again.").format(URL)
            exit(1)
            
    if len(offers_to_display) == 0:
        print("No offers were found.")
        exit(0)
    display_offers()

    if interactive:
        def select_offer(query):
            try:
                offer_url = offers_to_display[query].url
                r_offer = urllib.urlopen(offer_url)
                r_soup = BeautifulSoup(r_offer, "lxml")
                
                columns = int(os.popen('stty size', 'r').read().split()[1])
                print("=" * columns)
                print(Colors.BOLD + offer_url + Colors.ENDC)
                import textwrap
                paragraphs = r_soup.find_all('p')
                for paragraph in paragraphs:
                    print(Colors.YELLOW)
                    # replace multiple blank lines with one, 
                    # and remove multiple ocnsecutive white spaces for better rendering
                    for par in textwrap.wrap(re.sub(r'\n+', '\n', ' '.join(paragraph.text.split())).strip(), columns - 1):
                        print(par)
                    print(Colors.ENDC)
                print("=" * columns)

            except IOError:
                print("There was an error opening \"{}\". " +
                "Please check your internet connection and try again.").format(offer_url)
                exit(1)
            
        first_time = 0
        while (True):
            if first_time > 0:
                display_offers()
            query = raw_input(Colors.UNDERLINE + "Enter your query (q/Q to quit):" + Colors.ENDC + " ")
            if (query.lower() == "q"):
                break
            if (int(query) < len(offers_to_display) and int(query) >= 0):
                select_offer(int(query))
            else:
                print("Wrong input, try again.")
            first_time += 1


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
        try:
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
        except IOError: 
            print("There was an error opening \"{}\". " +
            "Please check your internet connection and try again.").format(URL)
            exit(1)


    if len(offers) == 0:
        exit(1)
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
    
def main():
    args = Args()
    if args.number_of_days:
        parse_days(args.number_of_days, args.filter_search, args.interactive_mode)

    else: # Default
        parse_pages(args.number_of_pages, args.filter_search, args.interactive_mode)

if __name__ == "__main__":
    main()
