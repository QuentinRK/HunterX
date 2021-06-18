from spyder.spiders import DealSpider
from terminaltables import AsciiTable
from config import config
from stdiomask import getpass
from passlib.hash import pbkdf2_sha256
import time
import sys
import psycopg2

"""
The Webscraper class process data supplied by the DealSpider class which scrapes data from web pages.
Adding, removing and displaying information from the database is another responsibility that this class has.

"""


class Webscraper:
    def __init__(self):
        self.search_result = None
        self.product_info = None
        self.option = None
        self.table_data = None
        self.params = config()
        self.validation_successful = False

    """
        The search function gathers the users input and passes that information down to the DealsSpider.
        This spider then returns the search results and the search function displays these options using the view_options function.
    """

    def search(self, search_text):
        try:
            search_spider = DealSpider(user_input=search_text, mode='initial')
            search_spider.run()
            self.search_result = search_spider.search_result 
            if self.search_result:
                print("\n"+ "Select an item below (for item [1] enter 1 etc..)" + "\n")
                self.view_options()
                while True:
                    self.selected_option = input().strip()
                    option_list = ['1', '2', '3']
                    if self.selected_option in option_list:
                        break
                    
                    if self.selected_option.lower() in ['q', 'quit', 'exit']:
                        sys.exit(0)

                    print("\n" + "Invalid input" + "\n") 
            else:
                print('Invalid Search Item')

        except IndexError:
            print('Invalid Input')
            sys.exit(1)

        
        self.price_list(self.selected_option)
        
    def view_options(self):
        if self.search_result:
            for i, results in enumerate(self.search_result, start=1):
                print('[' +str(i)+ ']' + ' ' + self.search_result[results]['name'] + '\n')
        else:
            print('Have not searched for any items')

    """
        The price list function runs an additional spider which takes the option that the user has selected.
        the return information is then tabulated for the user
    """

    def price_list(self, option):

        product_spider = DealSpider(optional_url=self.search_result[int(option)]['link'],
        mode='price_scrape')

        self.product_info = product_spider.product_info

        product_spider.run()

        table_data = [
            ['Company','Product','Price','Stock']
        ]

        count = 0
        for i in self.product_info:
             
            stock = self.product_info[i]['stock']
            name = self.product_info[i]['name']
            price = self.product_info[i]['price']
            company = self.product_info[i]['company']

            items = [company, name, price, stock]
            table_data.append(items)
            count +=1
        
        table = AsciiTable(table_data)   
        print('\n'+ table.table + '\n',
              '\n' + f'Found {count} Matches' + '\n')

        self.table_data = table_data[1:]

    """
        The save deals function connects to the database and inputs information such as the company, price and stock.
        Once user validation has been completed all of these processes take action and the deals table in the database is filled 
    """

    def save_deals(self,item):

        self.search(item)

        with psycopg2.connect(**self.params) as conn:
            with conn.cursor() as cur:

                username = input("\n"+"Enter Username: ").strip()
                validated = self.validate_user(username, mode="search")
                if validated:
                    data  = self.table_data
                    cheapest_deal = True
                    for field in data:
    
                        company = field[0]
                        product = field[1]
                        price =   field[2].strip('£')
                        stock =   field[3]
                
                        # Check for items in database 
                        # If they aren't add them to the database 
                        product_name_query = """SELECT name FROM products WHERE name=%s"""
                        cur.execute(product_name_query, (product,))
                        product_names = cur.fetchall()
            
                        company_name_query ="""SELECT name FROM companies WHERE name=%s"""
                        cur.execute(company_name_query, (company,))
                        company_names = cur.fetchall()
                        if (company_names == []):
                            insert_query = """INSERT INTO companies (name) VALUES (%s);"""
                            cur.execute(insert_query, (company,))
                        if (product_names == []):
                            insert_query = """INSERT INTO products (name, stock) VALUES (%s, %s);"""
                            cur.execute(insert_query, (product, stock))

                        # Check deal is already saved otherwise insert a product that is in stock
                        if stock and cheapest_deal:
                            check_product_query = """SELECT (users.id, deals.product_id) FROM deals 
                                             INNER JOIN users ON deals.user_id = users.id
                                             WHERE name=%s AND product_name=%s"""


                            cur.execute(check_product_query, (username,product))
                            product_id = cur.fetchone()

                            if product_id is None:
                                deals_query = """INSERT INTO deals (user_id, product_id, product_name, company_id,price)
                                                VALUES (
                                                    (SELECT id FROM users WHERE name=%s),
                                                    (SELECT id FROM products WHERE name=%s),
                                                    (SELECT name FROM products WHERE name=%s),
                                                    (SELECT id FROM companies WHERE name=%s), %s)"""
                                cur.execute(deals_query, (username, product, product, company, price))
                                cheapest_deal = False
                                print("Cheapest Deal Saved!")
                            else:
                                cheapest_deal = False
                                print("Deal Is Already Saved")

    """
        Queries the Deals table in the database and returns all of the users deals which is then tabulated.
    """

    def view_deals(self, user):
        validated = self.validate_user(user=user)
        if validated:
            with psycopg2.connect(**self.params) as conn:
                with conn.cursor() as cur:               
                    view_deals_query = """SELECT (companies.name), (product_name), (price::numeric) FROM deals
                                    INNER JOIN companies ON companies.id=deals.company_id
                                    INNER JOIN users ON users.id=deals.user_id
                                    where users.name=%s"""

                    headers = ['Company', 'Product', 'Price']
                    cur.execute(view_deals_query, (user,))
                    items  = cur.fetchall()
                    convert_tuple = [list(items[i]) for i in range(len(items))]
                    convert_tuple.insert(0, headers)
                    table = AsciiTable(convert_tuple)
                    print(table.table + "\n")

                            
            conn.close()

    def clear_deals(self, user):
        validated = self.validate_user(user)
        if validated:
            with psycopg2.connect(**self.params) as conn:
                with conn.cursor() as cur:
                        delete_query = """DELETE FROM deals WHERE user_id=(SELECT id FROM users WHERE name=%s)"""
                        cur.execute(delete_query, (user,))
                        print("Table Cleared!")


            conn.close()

    """
        This function queries the Users table to check if the user is in the database.
        Once this has completed the password validator function is called to validate the password of a new or existing user
    """

    def validate_user(self, user, mode=None):
        user = user.strip()
        with psycopg2.connect(**self.params) as conn:
           with conn.cursor() as cur:
                validation_query  = """SELECT name FROM users WHERE name=%s"""

                cur.execute(validation_query, (user,))
                name = cur.fetchone()
                if name is None:
                   if (mode == "search"):
                       print("\n"+'New User Please Fill Out Details' + "\n")
                       self.password_validator(user, mode="create")
                       return self.validation_successful
                   else:
                       print("Error: User Does Not Exist!")
                       sys.exit()
                    
                self.password_validator(user=user, mode="check")
                return self.validation_successful
    
    """
        Cascade deletes are executing when this function is run.
    """

    def delete_account(self, user):

        validated = self.validate_user(user)
        if validated:
            with psycopg2.connect(**self.params) as conn:
                with conn.cursor() as cur:
                    delete_account_query = """DELETE FROM users WHERE name=%s"""
                    cur.execute(delete_account_query, (user,))
                    print("Account Deleted!")
            conn.close()

    def password_validator(self, user, mode=None):        
            username = user.strip()

            with psycopg2.connect(**self.params) as conn:
                with conn.cursor() as cur:
                    attempts = 3
                    while attempts > 0 :
                        if mode == "create":
                            password = getpass(prompt="Password: ").strip()
                            confirm_password = getpass(prompt="Confirm Password: ").strip()

                            if (password == "") or (confirm_password == ""):
                                sys.exit()
                             
                            if password == confirm_password:
                                hashedpw = pbkdf2_sha256.hash(password)
                                new_user_query = "INSERT INTO users (name, password) VAlUES (%s, %s)"
                                cur.execute(new_user_query, (username, hashedpw))
                                self.validation_successful = True
                                break

                            

                            attempts -= 1
                            print("Passwords Do Not Match" + "\n" + f"{attempts} Attempts Left")
                            continue
                           

                        if mode == "check":
                            password = getpass(prompt="Password: ").strip()
                            if (password == ""):
                                sys.exit()

                            pw_query = "SELECT password FROM users WHERE name=%s;"
                            cur.execute(pw_query, (username,))
                            database_pw = cur.fetchone()
                            hashedpw = pbkdf2_sha256.hash(password)  
                            validation = pbkdf2_sha256.verify(password, database_pw[0])
                            attempts -=1
                            if validation:
                                print("Login Sucessful")
                                self.validation_successful = True
                                break
                        
                            continue

                        return self.validation_successful                   
            conn.close()

if __name__ == '__main__':
    Webscraper()