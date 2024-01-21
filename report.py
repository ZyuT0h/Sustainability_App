import shelve

class MonthlyReport:
    def __init__(self, month, sales, most_profitable_product, donations):
        self.month = month
        self.sales = sales
        self.most_profitable_product = most_profitable_product
        self.donations = donations

def get_report_data(month):
    # Replace this with your actual data retrieval logic
    # For simplicity, using a hardcoded example
    sales_data = {"Product A": 100, "Product B": 150, "Product C": 80}
    most_profitable_product = max(sales_data, key=sales_data.get)
    donation_data = {"Donation A": 200, "Donation B": 300, "Donation C": 150}

    return MonthlyReport(month, sales_data, most_profitable_product, donation_data)

def save_report(month, report):
    # Using shelve for simplicity (replace with a proper database in a real-world scenario)
    with shelve.open('reports.db') as db:
        db[month] = report

def load_report(month):
    with shelve.open('reports.db') as db:
        return db.get(month)
