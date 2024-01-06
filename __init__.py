from flask import Flask, render_template, request, redirect, url_for, jsonify
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


@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')


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


@app.route('/adminLogin')
def admin_login():
    return render_template('adminLogin.html')


@app.route('/shop')
def shop():
    return render_template('shop.html')


@app.route('/cart')
def cart():
    return render_template('cart.html')

staff_data = [
    {'staff_id': '1', 'email': 'staff1@example.com'},
    {'staff_id': '2', 'email': 'staff2@example.com'},
    # ...
]

@app.route('/staff_profile')
def staff_profiles():
    return render_template('staff_profile.html', staff_data=staff_data)

@app.route('/update_staff/<staff_id>', methods=['GET', 'POST'])
def update_staff(staff_id):
    if request.method == 'POST':
        update_staff_email = request.form['updateStaffEmail']
        # Update staff email in staff_data
        for staff in staff_data:
            if staff['staff_id'] == staff_id:
                staff['email'] = update_staff_email
        return redirect('/staff_profiles')
    return render_template('update_staff_profile.html', staff_id=staff_id)

@app.route('/update_staff_profile/<staff_id>', methods=['POST'])
def update_staff_profile(staff_id):
    update_staff_email = request.form['updateStaffEmail']

    # Find the staff member in staff_data and update the email
    for staff in staff_data:
        if staff['staff_id'] == staff_id:
            staff['email'] = update_staff_email
            break

    return redirect('/staff_profile')

@app.route('/delete_staff/<staff_id>')
def delete_staff(staff_id):
    # Delete staff profile from staff_data
    global staff_data
    staff_data = [staff for staff in staff_data if staff['staff_id'] != staff_id]
    return redirect(url_for('staff_profiles'))

# Example orders dictionary (Replace this with your actual order storage)
orders = {
    'customer1': {'order_quantity': 5, 'total_spending': 100, 'order_status': 'Completed'},
    'customer2': {'order_quantity': 8, 'total_spending': 200, 'order_status': 'Pending'},
}


@app.route('/order_details')
def order_details():
    order_data = []

    for customer_id, order_info in orders.items():
        order_data.append({
            'customer_id': customer_id,
            'order_quantity': order_info['order_quantity'],
            'total_spending': order_info['total_spending'],
            'order_status': order_info['order_status']
        })

    return render_template('order_details.html', orders=order_data)


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
    comments = get_comments()
    return render_template('forum.html', comments=comments)


@app.route('/submit_comment', methods=['POST'])
def submit_comment():
    data = request.get_json()
    username = "someusername"  # Replace with the actual username after it can be retrieved

    # Save the comment to the shelve file
    save_comment(username, data['subject'], data['message'])

    # Respond with the updated comments
    comments = get_comments()
    response_data = {'status': 'success', 'comments': comments}
    return jsonify(response_data)


def get_comments():
    # Open the shelve file and retrieve comments
    with shelve.open('comments.db') as db:
        comments = db.get('comments', [])
    return comments


def save_comment(username, subject, message):
    # Open the shelve file, retrieve existing comments, add the new comment, and save it
    with shelve.open('comments.db') as db:
        comments = db.get('comments', [])
        comments.append({'username': username, 'subject': subject, 'message': message})
        db['comments'] = comments


@app.route('/updatePoints')
def points():
    return render_template('updatePoints.html')


@app.route('/adminForum')
def admin_forum():
    # Retrieve comments for the admin forum
    comments = get_comments()

    return render_template('adminForum.html', comments=comments, admin=True)


@app.route('/submit_reply', methods=['POST'])
def submit_reply():
    data = request.get_json()
    comment_id = data.get('commentId')
    reply_content = data.get('replyContent')

    # Process and store the reply data as needed
    # For example, you can store it in the same comments.db file

    response_data = {'status': 'success', 'message': 'Reply submitted successfully'}
    return jsonify(response_data)


if __name__ == '__main__':
    app.run(debug=True)
