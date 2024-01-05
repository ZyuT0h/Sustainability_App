from flask import Flask, render_template, request, redirect, url_for
from Forms import CreateProductForm
import shelve, Product

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/homeUser')
def home_user():
    return render_template('homeUser.html')

@app.route('/homeAdmin')
def home_admin():
    return render_template('homeAdmin.html')

@app.route('/userLogin')
def user_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email == 'user@example.com' and password == 'password':
            return 'Login Successful!'
        else:
            return 'Login Failed. Invalid credentials.'
    return render_template('userLogin.html')


@app.route('/adminLogin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        staff_id = request.form['staff_id']
        password = request.form['password']
        
        if staff_id == 'staff123' and password == 'password':
            return 'Login Successful!'
        else:
            return 'Login Failed. Invalid credentials.'
    return render_template('adminLogin.html')


@app.route('/shop')
def shop():
    return render_template('shop.html')

@app.route('/cart')
def cart():
    return render_template('cart.html')


@app.route('/addProduct', methods=['GET', 'POST'])
def add_product():
    create_product_form = CreateProductForm(request.form)
    if request.method == 'POST' and create_product_form.validate():
        products_dict = {}
        db = shelve.open('product.db', 'c')
        try:
            products_dict = db['Products']
        except:
            print('Error in retrieving Products from product.db.')
        product = Product.Product(create_product_form.product_name.data,
                                  create_product_form.category.data,
                                  create_product_form.stock.data,
                                  create_product_form.price.data,
                                  create_product_form.description.data)
        products_dict[product.get_product_id()] = product
        db['Products'] = products_dict
        db.close()
        return redirect(url_for('manage_inventory'))
    return render_template('addProduct.html', form=create_product_form)


@app.route('/manageInventory')
def manage_inventory():
    products_dict = {}
    db = shelve.open('product.db', 'r')
    products_dict = db['Products']
    db.close()

    products_list = []
    for key in products_dict:
        product = products_dict.get(key)
        products_list.append(product)

    return render_template('manageInventory.html', count=len(products_list), products_list=products_list)


@app.route('/updateProduct/<int:id>/', methods=['GET', 'POST'])
def update_product(id):
    update_product_form = CreateProductForm(request.form)
    if request.method == 'POST' and update_product_form.validate():
        products_dict = {}
        db = shelve.open('product.db', 'w')
        products_dict = db['Products']
        product = products_dict.get(id)
        product.set_product_name(update_product_form.product_name.data)
        product.set_category(update_product_form.category.data)
        product.set_stock(update_product_form.stock.data)
        product.set_price(update_product_form.price.data)
        product.set_description(update_product_form.description.data)
        db['Products'] = products_dict
        db.close()
        return redirect(url_for('manage_inventory'))
    else:
        products_dict = {}
        db = shelve.open('product.db', 'r')
        products_dict = db['Products']
        db.close()
        product = products_dict.get(id)
        update_product_form.product_name.data = product.get_product_name()
        update_product_form.category.data = product.get_category()
        update_product_form.stock.data = product.get_stock()
        update_product_form.price.data = product.get_price()
        update_product_form.description.data = product.get_description()
        return render_template('updateProduct.html', form=update_product_form)


@app.route('/deleteProduct/<int:id>', methods=['POST'])
def delete_product(id):
    products_dict = {}
    db = shelve.open('product.db', 'w')
    products_dict = db['Products']
    products_dict.pop(id)
    db['Products'] = products_dict
    db.close()

    return redirect(url_for('manage_inventory'))


@app.route('/forum')
def forum():
    return render_template('forum.html')


if __name__ == '__main__':
    app.run(debug=True)
