from flask import Flask, render_template, request, redirect, url_for

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


if __name__ == '__main__':
    app.run(debug=True)
