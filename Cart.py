class Cart:
    def __init__(self):
        self.__items = {}

    def add_item(self, product, quantity):
        if product.get_product_id() in self.__items:
            self.__items[product.get_product_id()]['quantity'] += quantity
        else:
            self.__items[product.get_product_id()] = {
                'name': product.get_product_name(),
                'price': float(product.get_price()),
                'quantity': quantity,
            }

    def remove_item(self, product_id):
        if product_id in self.__items:
            del self.__items[product_id]

    def get_items(self):
        return self.__items.values()

    def get_total(self):
        total = 0
        for item in self.__items.values():
            total += item['price'] * item['quantity']
        return total
