class Customer:
    count_id = 0

    def __init__(self, email, password, postalcode, address, unit_no):
        Customer.count_id += 1
        self.__customer_id = Customer.count_id
        self.__email = email
        self.__password = password
        self.__postal_code = postalcode
        self.__address = address
        self.__unit_no = unit_no

    def get_customer_id(self):
        return self.__customer_id

    def set_customer_id(self, customer_id):
        self.__customer_id = customer_id

    def get_email(self):
        return self.__email

    def set_email(self, email):
        self.__email = email

    def get_password(self):
        return self.__password

    def set_password(self, password):
        self.__password = password

    def get_postalcode(self):
        return self.__postal_code

    def set_postalcode(self, postalcode):
        self.__postal_code = postalcode

    def get_address(self):
        return self.__address

    def set_address(self, address):
        self.__address = address

    def get_unit_no(self):
        return self.__unit_no

    def set_unit_no(self, unit_no):
        self.__unit_no = unit_no


class Points(Customer):
    def __init__(self, email, password, postalcode, address, unit_no, pts_collected, pts_redeemed, pts_left):
        super().__init__(email, password, postalcode, address, unit_no)
        self.pts_collected = pts_collected
        self.pts_redeemed = pts_redeemed
        self.pts_left = pts_left
        self.pts_collected = pts_collected
        self.pts_redeemed = pts_redeemed
        self.pts_left = pts_left

    def get_customer_id(self):
        return super().get_customer_id()

    def get_pts_collected(self):
        return self.pts_collected

    def set_pts_collected(self, pts_collected):
        self.pts_collected = pts_collected

    def get_pts_redeemed(self):
        return self.pts_redeemed

    def set_pts_redeemed(self, pts_redeemed):
        self.pts_redeemed = pts_redeemed

    def get_pts_left(self):
        return self.pts_left

    def set_pts_left(self, pts_left):
        self.pts_left = pts_left
