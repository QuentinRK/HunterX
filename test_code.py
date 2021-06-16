#!/usr/bin/env python3

from spyder.spiders import DealSpider
import time
import sys
import argparse



# user_response = input("Search Item (Be explicit): ").strip()


# spider = DealSpider(user_input=user_response, mode='initial')

# spider.run()

# search_result  = spider.search_result


# print()

# print("Select an item below (for item [1] enter 1 etc..) \n")


# for i, results in enumerate(search_result, start=1):

#     print('[' +str(i)+ ']' + ' ' + search_result[results]['name'], end="\n")


# print()

# while True:

#     option = (input().strip())

#     option_list = ['1', '2', '3']

#     if option in option_list:

#         break

#     elif option.lower() in ['q', 'quit', 'exit']:

#         sys.exit()

#     else:

#         print("Invalid input try again or to quit enter q")


# # join base url with this url 


# new_spider = DealSpider(optional_url=search_result[int(option)]['link'],
# mode='price_scrape')

# info = new_spider.info

# new_spider.run()


# count = 0

# for i in info:

    

#     stock = info[i]['stock']

#     name = info[i]['name']

#     price = info[i]['price']

#     company = info[i]['company']


#     print("Company: " + company +'|'+' Name: ' + name + '|' +' Price: '+ price +'|'+ '
# Stock: '+ str(stock),end='\n\n')

#     count +=1


# print(f'Found {count} matches', end='\n')


if __name__ == "__main__":
    main()

    



        


