#!/usr/bin/env python3
from webscraper import Webscraper
import argparse


scraper = Webscraper()
def Main():
    parser = argparse.ArgumentParser()

    parser.add_argument("search", help="Use this flag and specify a product you want to search",
                        type=str,
                        action="store")

    parser.add_argument("-s", "--save", help="Save the best deal to the database",
                        action="store_true")

    args = parser.parse_args()
    scraper.search(args.search)

    if args.save:
        scraper.save_deals(args.search)


if __name__ == "__main__":
    Main()

