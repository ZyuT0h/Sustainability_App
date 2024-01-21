from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from Forms import CreateProductForm, CreatePointForm
from datetime import datetime, timedelta
from Customer import Points
import re
import Product, Customer
import shelve
import bcrypt

app = Flask(__name__)
app.secret_key = 'something'


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/homeUser')
def home_user():
    return render_template('homeUser.html')


@app.route('/homeAdmin')
def home_admin():
    return render_template('homeAdmin.html')

# Open the shelve file in writeback mode for registration
@app.route('/register', methods=['GET', 'POST'])
def register():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            postal_code = request.form['postalCode']
            shipping_address = request.form['shippingAddress']
            unit_number = request.form['unitNo']

            # Hash the password before storing it
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            # Store customer data in a dictionary
            customer_info = {
                'email': email,
                'password': hashed_password,
                'postal_code': postal_code,
                'shipping_address': shipping_address,
                'unit_number': unit_number
            }

            # Open the shelve file in writeback mode
            with shelve.open('customer_db', writeback=True) as db:
                db[email] = customer_info  # Store customer_info in the shelve database with email as key

                print(f"Registered details for {email}: {customer_info}")

            return redirect('/')

        return render_template('register.html')

def show_registered_customers():
    with shelve.open('customer_db', 'r') as db:
        with open('registered_customers.txt', 'w') as file:
            file.write("Registered Customers:\n")
            for key in db:
                file.write(f"Customer: {key}")
                file.write(str(db[key]) + "\n")

# Call this function to display registered customers
show_registered_customers()

@app.route('/userLogin', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email == 'user@example.com' and password == 'password':
            return 'Login Successful!'
        else:
            return 'Login Failed. Invalid credentials.'
    return render_template('userLogin.html')

# Route for staff to log in
@app.route('/adminLogin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        entered_email = request.form['email']
        entered_password = request.form['password']

        staff_data = get_staff_data()

        # Check if the entered email exists in the staff data
        staff = next((s for s in staff_data if s['email'] == entered_email), None)

        if staff:
            stored_hashed_password = staff.get('password', None)
            password_changed = staff.get('password_changed', False)

            if stored_hashed_password and bcrypt.checkpw(entered_password.encode('utf-8'),
                                                         stored_hashed_password.encode('utf-8')):
                # Passwords match - log the staff in
                session['email'] = entered_email

                if not password_changed:
                    # User has not changed the password, prompt them to change it
                    flash('Welcome! Please set your password.', 'password_change_prompt')
                    return redirect('/change_password')
                else:
                    # Successful login, redirect to staff profile or other page
                    return redirect('/homeAdmin')  # You might need to adjust this based on your routes
            else:
                # Incorrect password
                flash('Incorrect password. Please try again.', 'error')
                return redirect('/adminLogin')
        else:
            # User does not exist
            flash('User does not exist. Please register or check your email.', 'error')
            return redirect('/adminLogin')

    return render_template('adminLogin.html')

# Route for staff to change their password
@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_new_password = request.form['confirm_new_password']

        # Retrieve the logged-in staff's email from the session
        logged_in_email = session.get('email')

        staff_data = get_staff_data()
        for staff in staff_data:
            if staff['email'] == logged_in_email:
                stored_hashed_password = staff.get('password', None)
                password_changed = staff.get('password_changed', False)

                if password_changed:
                    # Password has already been changed, redirect to staff profile or other page
                    return redirect('/staff_profile')

                # If the password hasn't been changed, verify the current password
                if stored_hashed_password and bcrypt.checkpw(current_password.encode('utf-8'),
                                                             stored_hashed_password.encode('utf-8')):
                    # Current password matches - update the password
                    if new_password == confirm_new_password:
                        # Check new password meets requirements
                        if len(new_password) < 8 or not re.search(r'[A-Z]', new_password) or \
                                not re.search(r'[a-z]', new_password) or not re.search(r'[0-9]', new_password) or \
                                not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
                            flash('Password must meet requirements.', 'error')
                            return redirect('/change_password')

                        # Hash the new password before storing it
                        hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode(
                            'utf-8')
                        staff['password'] = hashed_new_password

                        # Update last_password_change_date to the current date
                        staff['last_password_change_date'] = datetime.now().strftime('%Y-%m-%d')

                        # Set password_changed flag to True
                        staff['password_changed'] = True

                        # Update staff_data in the database
                        with open_staff_db() as db:
                            db['staff_data'] = staff_data

                        flash('Password changed successfully!', 'success')
                        return redirect('/homeAdmin')
                    else:
                        flash('New passwords do not match. Please try again.')
                        return redirect('/change_password')
                else:
                    flash('Incorrect current password.', 'error')
                    return redirect('/change_password')

    return render_template('change_password.html')

@app.route('/check_current_password', methods=['POST'])
def check_current_password():
    current_password = request.get_json().get('current_password', '')

    # Retrieve the logged-in staff's email from the session
    logged_in_email = session.get('email', '')

    # Retrieve the staff data from your database
    staff_data = get_staff_data()

    # Find the staff member with the logged-in email
    staff = next((s for s in staff_data if s['email'] == logged_in_email), None)

    if staff:
        stored_hashed_password = staff.get('password', None)
        if stored_hashed_password and bcrypt.checkpw(current_password.encode('utf-8'),
                                                     stored_hashed_password.encode('utf-8')):
            return jsonify(success=True)

    return jsonify(success=False)
@app.route('/shop')
def shop():
    return render_template('shop.html')


@app.route('/cart')
def cart():
    return render_template('cart.html')

# Open the shelve file for staff profiles
def open_staff_db():
    return shelve.open('staff_db')

# Retrieve staff data from the shelve file
def get_staff_data():
    with open_staff_db() as db:
        if 'staff_data' not in db:
            db['staff_data'] = []  # Initialize staff_data if not present in the shelve file
        return db['staff_data']

# Display staff profiles
@app.route('/staff_profile')
def staff_profiles():
    staff_data = get_staff_data()
    return render_template('staff_profile.html', staff_data=staff_data)

# Update staff profile
@app.route('/update_staff/<staff_id>', methods=['GET', 'POST'])
def update_staff(staff_id):
    if request.method == 'POST':
        update_staff_email = request.form['updateStaffEmail']
        update_staff_name = request.form['updateStaffName']
        update_staff_phone = request.form['updateStaffPhone']
        staff_data = get_staff_data()
        for staff in staff_data:
            if staff['staff_id'] == staff_id:
                staff['email'] = update_staff_email
                staff['name'] = update_staff_name
                staff['phone'] = update_staff_phone
                with open_staff_db() as db:
                    db['staff_data'] = staff_data  # Update the staff data in the shelve file
                break
        return redirect('/staff_profile')  # Redirect to staff profile page after successful update
    return render_template('update_staff_profile.html', staff_id=staff_id)

# Delete staff profile
@app.route('/delete_staff/<staff_id>')
def delete_staff(staff_id):
    staff_data = get_staff_data()
    staff_data = [staff for staff in staff_data if staff['staff_id'] != staff_id]
    with open_staff_db() as db:
        db['staff_data'] = staff_data
    return redirect('/staff_profile')


# Register new staff profile
@app.route('/register_staff', methods=['GET', 'POST'])
def register_staff():
    if request.method == 'POST':
        new_staff_email = request.form['email']
        new_staff_name = request.form['name']
        new_staff_phone = request.form['phone']
        staff_data = get_staff_data()
        new_staff_id = str(len(staff_data) + 1)

        # Hashing the default password (e.g., 'password123')
        default_password = 'password123'
        hashed_password = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        staff_data.append({
            'staff_id': new_staff_id,
            'email': new_staff_email,
            'name': new_staff_name,
            'phone': new_staff_phone,
            'password': hashed_password  # Storing hashed password
        })

        with open_staff_db() as db:
            db['staff_data'] = staff_data

        return redirect('/staff_profile')  # Redirect to staff profile page after successful registration

    return render_template('register_staff.html')


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
    username = "C_username"  # Replace with the actual username after it can be retrieved

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


@app.route('/adminForum')
def admin_forum():
    # retrieve comments for the admin side forum
    comments = get_comments()

    return render_template('adminForum.html', comments=comments, admin=True)


@app.route('/delete_comment', methods=['POST'])
def delete_comment():
    data = request.get_json()
    comment_index = int(data['comment_index'])

    # Delete the comment with the specified index
    delete_comment_by_index(comment_index)

    # Respond with the updated comments
    comments = get_comments()
    response_data = {'status': 'success', 'comments': comments}
    return jsonify(response_data)


def delete_comment_by_index(index):
    # Open the shelve file, retrieve existing comments, delete the comment by index, and save it
    with shelve.open('comments.db') as db:
        comments = db.get('comments', [])
        if 0 <= index < len(comments):
            del comments[index]
            db['comments'] = comments


@app.route('/add_cus_ptss', methods=['GET', 'POST'])
def add_cus_ptss():
    add_cus_pts_form = CreatePointForm(request.form)
    if request.method == "POST" and add_cus_pts_form.validate():
        add_pts_dict = {}
        db = shelve.open('points.db', 'c')
        try:
            add_pts_dict = db['Points']
        except:
            print("Error in retrieving points from points.db")

        points = Points(
            pts_collected=add_cus_pts_form.pts_collected.data,
            pts_redeemed=add_cus_pts_form.pts_redeemed.data,
            pts_left=add_cus_pts_form.pts_left.data)

        add_pts_dict[points.get_customer_id()] = points
        db['Points'] = add_pts_dict

        db.close()

        return redirect(url_for('point_system'))
    return render_template('add_cus_ptss.html', form=add_cus_pts_form)


@app.route('/pointSystem')
def point_system():
    points_dict = {}
    db = shelve.open('points.db', 'r')
    points_dict = db['Points']
    db.close()

    points_list = []
    for key in points_dict:
        points = points_dict[key]
        points_list.append(points)

    return render_template('pointSystem.html', count=len(points_list), points_list=points_list)


@app.route('/edit_points/<int:id>', methods=['GET', 'POST'])
def edit_points(id):
    update_points_form = CreatePointForm(request.form)
    points_dict = {}

    if request.method == 'POST' and update_points_form.validate():
        db = shelve.open('points.db', 'w')
        points_dict = db['Points']

        pointU = points_dict.get(id)
        if pointU:
            pointU.set_pts_collected(update_points_form.pts_collected.data)
            pointU.set_pts_redeemed(update_points_form.pts_redeemed.data)
            pointU.set_pts_left(update_points_form.pts_left.data)

            db['Points'] = points_dict
            db.close()

        return redirect(url_for('point_system'))
    else:
        db = shelve.open('points.db', 'r')
        points_dict = db['Points']
        db.close()

        pointU = points_dict.get(id)
        if pointU:
            update_points_form.pts_collected = pointU.get_pts_collected()
            update_points_form.pts_redeemed = pointU.get_pts_redeemed()
            update_points_form.pts_left = pointU.get_pts_left()

            return render_template('edit_points.html', form=update_points_form)
    return "Invalid ID/ data not found"

@app.route('/delete_points/<string:cust_id>', methods=['GET', 'POST'])
def delete_points(cust_id):
   return render_template('')


if __name__ == '__main__':
    app.run(debug=True)
