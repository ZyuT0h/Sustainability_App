class Customer:
    count_id = 0

    def __init__(self):
        Customer.count_id += 1
        self.__customer_id = Customer.count_id

    def get_customer_id(self):
        return self.__customer_id

    def set_customer_id(self, customer_id):
        self.__customer_id = customer_id


class Points(Customer):
    def __init__(self, pts_collected, pts_redeemed, pts_left):
        super().__init__()
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
