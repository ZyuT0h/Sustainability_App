from flask import Flask, render_template, request, redirect, url_for
from forms import CreateUserForm

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
    return render_template('userLogin.html')


@app.route('/adminLogin')
def admin_login():
    return render_template('adminLogin.html')


@app.route('/shop')
def shop():
    return render_template('shop.html')


@app.route('/addProduct')
def add_products():
    return render_template('addProduct.html')


@app.route('/cart')
def cart():
    return render_template('cart.html')


@app.route('/manageInventory')
def manage_inventory():
    return render_template('manageInventory.html')


@app.route('/forum')
def forum():
    return render_template('forum.html')


@app.route('/CreateUser', methods=['GET', 'POST'])
def create_user():
    create_user_form = CreateUserForm(request.form)
    if request.method == 'POST' and create_user_form.validate():
        return redirect(url_for('home'))
    return render_template('CreateUser.html', form=create_user_form)


if __name__ == '__main__':
    app.run()
