#!/usr/bin/env python3
from webscraper import Webscraper
from docopt import docopt

usage = """

HunterX CLI

Usage:
    main.py search <item> [-s] [-h]
    main.py view <user> [-h] [-d]
    main.py account <user> [-d] [-up]

Options:
    -h --help
    -s --save               Save search results to account
    -d --delete             Deletes item from database


"""

def Main():

    args = docopt(usage)
    scraper = Webscraper()

    if args['search']:
        item = args['<item>']
        if args['--save']:
            scraper.save_deals(item)
        else:
            scraper.search(item)

    if args['view']:
        if args['--delete']:
            scraper.clear_deals(args['<user>'])
        else:
            scraper.view_deals(args['<user>'])

        

    if args['account']:
        user = args['<user>']
        if args['--delete']:
            scraper.delete_account(user)
      

if __name__=='__main__':
    Main()
