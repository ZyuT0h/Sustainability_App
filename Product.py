import shelve

class Product:

    def __init__(self, product_name, category, stock, price, description):
        # Open the shelve storage
        db = shelve.open('product_id_list.db', 'c')

        # Retrieve the list of product IDs from the storage or initialize an empty list
        product_id_list = db.get('ProductId', [])

        # Start with an initial product ID of 1
        count_id = 1
        while count_id in product_id_list:
            # If the count_id is in the list, increment it by 1
            count_id += 1
        self.__product_id = count_id
        product_id_list.append(count_id)
        db['ProductId'] = product_id_list
        db.close()
        self.__product_name = product_name
        self.__product_image = None
        self.__category = category
        self.__stock = stock
        self.__price = price
        self.__description = description

    def set_product_id(self, product_id):
        self.__product_id = product_id

    def set_product_name(self, product_name):
        self.__product_name = product_name
        
    def set_product_image(self, product_image):
        self.__product_image = product_image

    def set_category(self, category):
        self.__category = category

    def set_stock(self, stock):
        self.__stock = stock

    def set_price(self, price):
        self.__price = price

    def set_description(self, description):
        self.__description = description

    def get_product_id(self):
        return self.__product_id

    def get_product_name(self):
        return self.__product_name

    def get_product_image(self):
        return self.__product_image

    def get_category(self):
        return self.__category

    def get_stock(self):
        return self.__stock
    
    def get_price(self):
        return self.__price

    def get_description(self):
        return self.__description
    