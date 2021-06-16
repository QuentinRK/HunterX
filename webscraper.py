from spyder.spiders import DealSpider
from terminaltables import AsciiTable
from config import config
from stdiomask import getpass
import time
import sys
import os
import psycopg2
import bcrypt
import stdiomask


class Webscraper:
    def __init__(self):
        self.search_result = None
        self.info = None
        self.option = None
        self.table_data = None

    def search(self, search_text):
        try:
            search_spider = DealSpider(user_input=search_text, mode='initial')
            search_spider.run()
            self.search_result = search_spider.search_result 
            if self.search_result:
                print("\n"+ "Select an item below (for item [1] enter 1 etc..)" + "\n")
                self.view_options()
                while True:
                    self.option = input().strip()
                    option_list = ['1', '2', '3']
                    if self.option in option_list:
                        break
                    
                    if self.option.lower() in ['q', 'quit', 'exit']:
                        sys.exit(0)

                    print("\n" + "Invalid input" + "\n") 
            else:
                print('Invalid Search Item')

        except IndexError:
            print('Invalid Input')
            sys.exit(1)

        
        self.price_list(self.option)
        
    def view_options(self):
        if self.search_result:
            for i, results in enumerate(self.search_result, start=1):
                print('[' +str(i)+ ']' + ' ' + self.search_result[results]['name'] + '\n')
        else:
            print('Have not searched for any items')

    def price_list(self,option):

        price_spider = DealSpider(optional_url=self.search_result[int(option)]['link'],
        mode='price_scrape')

        self.info = price_spider.info

        price_spider.run()

        table_data = [
            ['Company','Item','Price','Stock']
        ]

        count = 0
        for i in self.info:
             
            stock = self.info[i]['stock']
            name = self.info[i]['name']
            price = self.info[i]['price']
            company = self.info[i]['company']

            items = [company, name, price, stock]
            table_data.append(items)
            count +=1
        
        table = AsciiTable(table_data)   
        print('\n'+ table.table + '\n',
              '\n' + f'Found {count} Matches' + '\n')

        self.table_data = table_data[1:]

    def save_deals(self,item):
        params = config()

        conn = psycopg2.connect(**params)

        cur = conn.cursor()

        username = input("\n"+"Enter Username: ").strip()

        username_query = "SELECT name FROM users WHERE name=%s"

        cur.execute(username_query, (username,))
        name = cur.fetchall()

        if name == []:

            print("\n"+'New User Please Fill Out Details' + "\n")
            validate_passwords = True

            while validate_passwords:

                password = getpass(prompt="Password: ").strip()
                confirm_password = getpass(prompt="Confirm Password: ").strip()

                if password == confirm_password:
                    break

                print("Passwords Do Not Match")
            
        
            bytes_pw = password.encode()
            hashed = bcrypt.hashpw(bytes_pw, bcrypt.gensalt())
            insert_user = "INSERT INTO users (name, password) VALUES (%s, %s)"
            cur.execute(insert_user, (username, hashed))
            print("New User Created")

        else:
            password = getpass(prompt="Password: ")
            pw_query = "SELECT encode(password, 'hex') FROM users WHERE name=%s;"
            cur.execute(pw_query, (username,))
            hashedpw = cur.fetchone()

            # if validation:
            #     print("Login Complete")

        conn.commit()
        cur.close()
        conn.close()
  



if __name__ == '__main__':
    Webscraper()