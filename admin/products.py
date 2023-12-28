class Product:
    count_id = 0

    def __init__(self, product_name, category, stock, price, description):
        product.count_id += 1
        self.__product_id = product.count_id
        self.__product_name = product_name
        self.__category = category
        self.__stock = stock
        self.__price = price
        self.__description = description


    def set_product_id(self, product_id):
        self.__product_id = product_id

    def set_product_name(self, product_name):
        self.__product_name = product_name

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

    def get_category(self):
        return self.__cetegory

    def get_stock(self):
        return self.__stock

    def get_description(self):
        return self.__description