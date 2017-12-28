#!/usr/bin/env python
# *- coding: utf-8 -*-

import argparse

class Args():
    def __init__(self):
        p = argparse.ArgumentParser(prog='letudiant-cli-offer-scrapper',
                description='Parse job/internship offers from letudiant, from the command-line.')

        p.add_argument('--days', type=int, 
                help='Number of days to parse.')

        p.add_argument('--interactive', action='store_true',
                help='Enable interactive mode.')

        p.add_argument('--pages', type=int, default=1,
                help='Number of pages to parse (1 by default).')

        p.add_argument('--new', action='store_true',
                help='Display only new offers (compared to a log file).')

        p.add_argument('--filter', action='append',
                help='Add filters to the gathered offers.')

        args = p.parse_args()

        self.number_of_days = args.days
        self.number_of_pages = args.pages
        self.interactive_mode= args.interactive
        self.new = args.new
        self.filter_search = args.filter
