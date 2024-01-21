# import shelve

class Product:
    count_id = 0

    def __init__(self, product_name, category, stock, price, description):
        Product.count_id += 1
        self.__product_id = Product.count_id
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
    