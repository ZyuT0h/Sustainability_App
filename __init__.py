from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from werkzeug.utils import secure_filename
import os
from Product import Product
from Cart import Cart
from datetime import datetime, timedelta
from report import MonthlyReport, get_report_data, save_report, load_report
from Forms import CreatePointForm
from Customer import Points
import random
import re
import shelve
import bcrypt
import uuid


app = Flask(__name__)
app.secret_key = 'something'


@app.route('/')
def home():
    return render_template('home.html')


def about():
    return render_template('about.html')


@app.route('/homeUser')
def home_user():
    return render_template('homeUser.html')


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
            customer_id = get_customer_id(email)
            if customer_id:
                session['customer_id'] = customer_id
                return redirect(url_for('homeUser'))
            else:
                flash('Failed to retrieve customer ID. Please try again.', 'error')
                return redirect(url_for('userLogin'))

        else:
            flash('Login Failed. Invalid credentials.', 'error')
            return redirect(url_for('userLogin'))
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
                session['staff_email'] = entered_email

                if not password_changed:
                    # User has not changed the password, prompt them to change it
                    flash('Welcome! Please set your password.', 'password_change_prompt')
                    return redirect('/change_password')
                else:
                    # Successful login, redirect to staff profile or other page
                    return redirect('/staff_profile')  # You might need to adjust this based on your routes
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
                    flash('Password has already been changed.', 'error')
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
    staff_data = get_staff_data()
    staff = next((s for s in staff_data if s['staff_id'] == staff_id), None)

    if request.method == 'POST':
        # Fetch the existing staff data for display
        existing_staff_data = get_staff_data()

        if staff:
            update_staff_email = request.form['updateStaffEmail']
            update_staff_name = request.form['updateStaffName']
            update_staff_phone = request.form['updateStaffPhone']
            update_staff_role = request.form['updateStaffRole']

            # Check if the email is already registered (excluding the current staff being updated)
            if any(s['email'] == update_staff_email and s['staff_id'] != staff_id for s in staff_data):
                flash("Email address is already registered.", "error")
                return render_template('update_staff_profile.html', staff=staff, staff_id=staff_id)

            staff['email'] = update_staff_email
            staff['name'] = update_staff_name
            staff['phone'] = update_staff_phone
            staff['role'] = update_staff_role

            with open_staff_db() as db:
                db['staff_data'] = staff_data  # Update the staff data in the shelve file

            return redirect('/staff_profile')  # Redirect to staff profile page after successful update

    # Fetch staff data for the specified staff_id
    if staff:
        return render_template('update_staff_profile.html', staff=staff, staff_id=staff_id)
    else:
        # Handle the case where staff with the given ID is not found
        flash("Staff not found", "error")
        return redirect('/staff_profile')


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
        new_staff_role = request.form['role']

        staff_data = get_staff_data()

        # Check if the email is already registered
        if any(staff['email'] == new_staff_email for staff in staff_data):
            flash("Email address is already registered.", "error")
            return render_template('register_staff.html')

        # Generate a unique staff ID based on the first few characters of the name and a random number
        new_staff_id = f"{new_staff_name[:3]}{random.randint(100, 999)}"

        # Check if the generated ID is already in use
        while any(staff['staff_id'] == new_staff_id for staff in staff_data):
            new_staff_id = f"{new_staff_name[:3]}{random.randint(100, 999)}"

        # Hashing the default password (e.g., 'password123')
        default_password = 'password123'
        hashed_password = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        staff_data.append({
            'staff_id': new_staff_id,
            'email': new_staff_email,
            'name': new_staff_name,
            'phone': new_staff_phone,
            'role': new_staff_role,
            'password': hashed_password # Storing hashed password
        })

        with open_staff_db() as db:
            db['staff_data'] = staff_data

        return redirect('/staff_profile')  # Redirect to staff profile page after successful registration

    return render_template('register_staff.html')

@app.route('/order_details')
def order_details():
    # Retrieve order details from session
    order_details = session.get('order_details')
    order_id = session.get('order_id')
    payment_time = session.get('payment_time')
    total_price = session.get('total_price')
    print("Order details in session:", order_details)
    print("Payment Time in Session:", payment_time)
    print("Total Price in Session:", total_price)

    return render_template('order_details.html', order=order_details, order_id=order_id, payment_time=payment_time, total_price=total_price)

@app.route('/staff_details')
def staff_details():
    # Retrieve staff email from session
    staff_email = session.get('staff_email')

    # Retrieve customer_id associated with staff_email from the database or wherever it's stored
    customer_id = retrieve_customer_id(staff_email)  # Example function to retrieve customer_id

    # Use customer_id to fetch and display relevant customer order details
    order_details = retrieve_order_details(customer_id)  # Example function to retrieve order details

    return render_template('staff_details.html', order_details=order_details)

@app.route('/generate_report/<month>')
def generate_report(month):
    report = get_report_data(month)
    save_report(month, report)
    return render_template('report.html', report=report)


@app.route('/view_report/<month>')
def view_report(month):
    report = load_report(month)
    return render_template('report.html', report=report)


@app.route('/report')
def report():
    # Replace this with your actual logic for generating the report
    report_data = {
        'month': 'January',
        'sales': {'Product A': 100, 'Product B': 150, 'Product C': 80},
        'most_profitable_product': 'Product B',
        'donations': {'Donation A': 200, 'Donation B': 300, 'Donation C': 150}
    }

    return render_template('report.html', report=report_data)


# Set the upload folder outside of the route function
# app.config['UPLOAD_FOLDER'] = 'product_images'

@app.route('/shop')
def shop():
    products_dict = {}
    db = shelve.open('product.db', 'r')
    products_dict = db['Products']
    db.close()

    products_list = []
    for key in sorted(products_dict):
        product = products_dict.get(key)
        products_list.append(product)

    categories_list = get_categories()
    return render_template('shop.html', products_list=products_list, categories_list=categories_list)


@app.route('/shop/<category>')
def category_page(category):
    if category == category:
        products_dict = {}
        db = shelve.open('product.db', 'r')
        products_dict = db['Products']
        db.close()

        products_list = [product for product in products_dict.values() if product.get_category() == category]
        categories_list = get_categories()
        return render_template('shop.html', products_list=products_list, categories_list=categories_list)


@app.route('/cart')
def cart():
    cart_items = session.get('cart', {})
    total_price = sum(float(item['price']) * int(item['quantity']) for item in cart_items.values())
    total_quantity = sum(item['quantity'] for item in cart_items.values())
    return render_template('cart.html', cart_items=cart_items, total_price=total_price,
                           total_quantity=total_quantity)


@app.route('/add_to_cart/<int:id>', methods=['POST'])
def add_to_cart(id):
    try:
        print(type(id))

        products_dict = {}
        db = shelve.open('product.db', 'r')
        products_dict = db['Products']
        db.close()

        print('Products Dictionary:', products_dict)  # Debug print

        product = products_dict.get(int(id))
        print('Retrieved product:', product)  # Add this line

        print("session:", session.keys())

        if 'cart' not in session:
            session['cart'] = {}

        print(session)
        print('Session:', session['cart'])
        # Print the types of values in the cart

        if product is not None:
            if 'cart' not in session:
                session['cart'] = {}
                print('Cart session created')

                # Print the session data to debug
                print('Session:', session['cart'])

            # Add the product to the cart
            cart = session['cart']
            print('Cart session retrieved:', cart)
            # Print the types of values in the cart

            if str(id) in cart:
                cart[str(id)]['quantity'] += 1
                cart[str(id)]['subtotal'] = cart[str(id)]['price'] * cart[str(id)]['quantity']
                print(f'Cart item {int(id)} +1')
            else:
                cart[str(id)] = {
                    'image': product.get_product_image(),
                    'name': product.get_product_name(),
                    'price': float(product.get_price()), # Ensure price is converted to float
                    'quantity': 1,
                    'subtotal': float(product.get_price()) * 1
                }
                print('New Cart item added')

            # Update the session cart
            session['cart'] = cart

            print('Cart content:', session['cart'])  # Print cart content for debugging
            print(session)

        else:
            print(f'Error: Product with ID {int(id)} not found')

        print('Cart content:', session['cart'])

    except Exception as e:
       print('Error:', e)  # Print any exceptions that occur

    return redirect(url_for('shop'))


@app.route('/remove_item_from_cart/<int:id>', methods=['POST'])
def remove_item_from_cart(id):
    try:
        cart = session['cart']

        if str(id) in cart:
            cart[str(id)]['quantity'] -= 1
            cart[str(id)]['subtotal'] = cart[str(id)]['price'] * cart[str(id)]['quantity']
            if cart[str(id)]['quantity'] == 0:
                del cart[str(id)]  # Remove the item from the cart if the quantity becomes zero

        session['cart'] = cart
        return redirect(url_for('cart'))

    except Exception as e:
        print('Error:', e)


@app.route('/add_item_to_cart/<int:id>', methods=['POST'])
def add_item_to_cart(id):
    try:
        cart = session['cart']

        if str(id) in cart:
            cart[str(id)]['quantity'] += 1
            cart[str(id)]['subtotal'] = cart[str(id)]['price'] * cart[str(id)]['quantity']

        session['cart'] = cart

        return redirect(url_for('cart'))

    except Exception as e:
        print('Error:', e)


@app.route('/clear_item/<int:id>', methods=['POST'])
def clear_item(id):
    try:
        cart = session.get('cart', {})

        if str(id) in cart:
            del cart[str(id)]  # Remove the specific item from the cart

        session['cart'] = cart

        return redirect(url_for('cart'))

    except Exception as e:
        print('Error:', e)


@app.route('/empty_cart', methods=['POST'])
def empty_cart():
    session.pop('cart', None)
    return redirect(url_for('cart'))


@app.route('/addCategory', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        category = request.form['categoryName']

        categories_dict = {}
        db = shelve.open('categories.db', 'c')
        try:
            categories_dict = db['Categories']
        except:
            print('Error in retrieving Categories from categories.db.')

        # Ensure category name is unique
        if category not in categories_dict:
            categories_dict[category] = category
            db['Categories'] = categories_dict
            db.close()
            return redirect(url_for('manage_category'))
    return render_template('addCategory.html')


@app.route('/getCategories')
def get_categories():
    categories_dict = {}
    db = shelve.open('categories.db', 'r')
    categories_dict = db['Categories']
    db.close()

    categories_list = []
    for key in categories_dict:
        category = categories_dict.get(key)
        categories_list.append(category)

    return categories_list


@app.route('/manageCategory')
def manage_category():
    categories_list = get_categories()
    return render_template('manageCategory.html', count=len(get_categories()), categories_list=categories_list)


@app.route('/deleteCategory/<string:category>', methods=['POST'])
def delete_category(category):
    categories_dict = {}
    db = shelve.open('categories.db', 'w')
    categories_dict = db['Categories']
    categories_dict.pop(category)
    db['Categories'] = categories_dict
    db.close()

    return redirect(url_for('manage_category'))


@app.route('/addProduct', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product = Product(
            product_name=request.form['productName'],
            category=request.form['category'],
            stock=request.form['stock'],
            price=request.form['price'],
            description=request.form['description'],
        )

        # Handle file upload
        if 'productImage' in request.files:
            file = request.files['productImage']
            if file.filename != '':
                # Save the file with a secure filename
                filename = secure_filename(file.filename)
                file.save(os.path.join('static', 'product_images', filename))
                product.set_product_image(filename)

        products_dict = {}
        db = shelve.open('product.db', 'c')
        try:
            products_dict = db['Products']
        except:
            print('Error in retrieving Products from product.db.')
        products_dict[product.get_product_id()] = product
        db['Products'] = products_dict
        db.close()

        return redirect(url_for('manage_inventory'))

    # Get the list of categories to pass to the template
    categories_list = get_categories()  # Custom function to get existing categories
    return render_template('addProduct.html', categories_list=categories_list)


@app.route('/manageInventory')
def manage_inventory():
    products_dict = {}
    db = shelve.open('product.db', 'r')
    products_dict = db['Products']
    db.close()

    products_list = []
    for key in sorted(products_dict):
        product = products_dict.get(key)
        products_list.append(product)

    categories_list = get_categories()

    return render_template('manageInventory.html', count=len(products_list),
                           products_list=products_list, categories_list=categories_list)


@app.route('/updateProduct/<int:id>/', methods=['GET', 'POST'])
def update_product(id):
    if request.method == 'POST':
        products_dict = {}
        db = shelve.open('product.db', 'w')
        products_dict = db['Products']
        product = products_dict.get(id)

        # Use request.form to get form data
        product.set_product_name(request.form['productName'])
        product.set_category(request.form['category'])
        product.set_stock(request.form['stock'])
        product.set_price(request.form['price'])
        product.set_description(request.form['description'])

        # Handle file upload
        if 'productImage' in request.files:
            file = request.files['productImage']
            if file.filename != '':
                # Delete the old image file
                old_image_path = os.path.join('static', 'product_images', product.get_product_image())
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)

                # Save the new file with a secure filename
                filename = secure_filename(file.filename)
                file.save(os.path.join('static', 'product_images', filename))
                product.set_product_image(filename)

        db['Products'] = products_dict
        db.close()

        return redirect(url_for('manage_inventory'))
    else:
        products_dict = {}
        db = shelve.open('product.db', 'r')
        products_dict = db['Products']
        db.close()
        product = products_dict.get(id)

        # Use request.form to populate form data
        product_name_data = product.get_product_name()
        category_data = product.get_category()
        stock_data = product.get_stock()
        price_data = product.get_price()
        description_data = product.get_description()

        categories_list = get_categories()

        return render_template('updateProduct.html', product_name_data=product_name_data,
                               category_data=category_data, stock_data=stock_data, price_data=price_data,
                               description_data=description_data, categories_list=categories_list)


@app.route('/deleteProduct/<int:id>', methods=['POST'])
def delete_product(id):
    products_dict = {}
    db = shelve.open('product.db', 'w')
    products_dict = db['Products']
    products_dict.pop(id)
    db['Products'] = products_dict
    db.close()

    db = shelve.open('product_id_list.db', 'w')
    product_id_list = db.get('ProductId', [])
    product_id_list.remove(id)
    db['ProductId'] = product_id_list
    db.close()

    return redirect(url_for('manage_inventory'))


@app.route('/forum')
def forum():
    comments = get_comments()
    return render_template('forum.html', comments=comments)


@app.route('/submit_comment', methods=['POST'])
def submit_comment():
    data = request.get_json()
    username = "Zac"  # Replace with the actual username after it can be retrieved

    # Save the comment to the shelve file
    save_comment(username, data['subject'], data['message'])

    # Respond with the updated comments
    comments = get_comments()
    response_data = {'status': 'success', 'comments': comments}
    return jsonify(response_data)


def get_comments():
    with shelve.open('comments.db') as db:
        comments = db.get('comments', [])
        for comment in comments:
            replies = comment.get('replies', [])
            comment['replies'] = replies
    return comments


def save_comment(username, subject, message):
    # Open the shelve file, retrieve existing comments, add the new comment, and save it
    with shelve.open('comments.db') as db:
        comments = db.get('comments', [])
        comments.append({'username': username, 'subject': subject, 'message': message})
        db['comments'] = comments


@app.route('/submit_reply', methods=['POST'])
def submit_reply():
    data = request.get_json()
    parent_comment_index = int(data['parent_comment_index'])
    reply_message = data['reply_message']

    add_reply(parent_comment_index, reply_message)

    comments = get_comments()
    response_data = {'status': 'success', 'comments': comments}
    return jsonify(response_data)


def add_reply(parent_comment_index, reply_message):
    with shelve.open('comments.db') as db:
        comments = db.get('comments', [])
        comments[parent_comment_index].setdefault('replies', []).append(reply_message)
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


@app.route('/edit_points/<int:cust_id>', methods=['GET', 'POST'])
def edit_points(cust_id):
    if request.method == "POST":
        # retrieve  data
        pts_collected_str = request.form['pts_collected']
        pts_redeemed_str = request.form['pts_redeemed']
        pts_left_str = request.form['pts_left']

        try:
            pts_collected = int(pts_collected_str)
            pts_redeemed = int(pts_redeemed_str)
            pts_left = int(pts_left_str)
        except ValueError:
            return render_template('edit_points.html', error="Please enter numerical values for all fields.",
                                   cust_id=cust_id, pts_collected=pts_collected_str,
                                   pts_redeemed=pts_redeemed_str, pts_left=pts_left_str)
        # validations
        if pts_collected < 0:
            return render_template('edit_points.html', error="Points collected cannot be negative.", cust_id=cust_id,
                                   pts_collected=pts_collected_str, pts_redeemed=pts_redeemed_str, pts_left=pts_left_str
                                   )
        if pts_redeemed < 0:
            return render_template('edit_points.html', error="Points redeemed cannot be negative.", cust_id=cust_id,
                                   pts_collected=pts_collected_str, pts_redeemed=pts_redeemed_str, pts_left=pts_left_str
                                   )
        if pts_left < 0:
            return render_template('edit_points.html', error="Points left cannot be negative.", cust_id=cust_id,
                                   pts_collected=pts_collected_str, pts_redeemed=pts_redeemed_str, pts_left=pts_left_str
                                   )

        # update data
        points_dict = {}
        db = shelve.open('points.db', writeback=True)
        points_dict = db['Points']

        rpoints = points_dict.get(cust_id)

        rpoints.set_pts_collected(pts_collected)
        rpoints.set_pts_redeemed(pts_redeemed)
        rpoints.set_pts_left(pts_left)

        db['Points'] = points_dict
        db.close()

        return redirect(url_for("point_system"))
    else:
        points_dict = {}
        db = shelve.open('points.db', 'r')
        points_dict = db['Points']
        db.close()

        rpoints = points_dict.get(cust_id)

        return render_template('edit_points.html', cust_id=cust_id, edited_cust_id=cust_id,
                               pts_collected=rpoints.get_pts_collected(), pts_redeemed=rpoints.get_pts_redeemed(),
                               pts_left=rpoints.get_pts_left())


@app.route('/delete_points/<int:cust_id>', methods=['POST'])
def delete_points(cust_id):
    db = shelve.open('points.db', 'w')
    points_dict = db.get('Points', {})

    # Check if cust_id exists in the dictionary before attempting to delete
    if cust_id in points_dict:
        points_dict.pop(cust_id)
        db['Points'] = points_dict
        db.close()
        print(f"Deletion successful for customer ID: {cust_id}")
    else:
        print(f"Customer ID {cust_id} not found in points_dict")

    return redirect(url_for('point_system'))


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
            pts_redeemed=add_cus_pts_form.pts_redeemed.data, pts_left=add_cus_pts_form.pts_left.data)

        add_pts_dict[points.get_customer_id()] = points
        db['Points'] = add_pts_dict

        db.close()

        return redirect(url_for('point_system'))
    return render_template('add_cus_ptss.html', form=add_cus_pts_form)

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    # Log session data before setting customer_id
    app.logger.info("Session data before setting customer_id: %s", session)

    # Set customer_id in session
    customer_id = session.get('customer_id')
    app.logger.info("Customer ID retrieved from session: %s", customer_id)

    # Set customer email in session
    customer_email = session.get('customer_email')
    app.logger.info("Customer email retrieved from session: %s", customer_email)

    # Log session data after setting customer_id
    session['customer_id'] = customer_id
    session['customer_email'] = customer_email
    app.logger.info("Session data after setting customer_id: %s", session)

    cart_items = session.get('cart', {})
    total_price = sum(float(item['price']) * int(item['quantity']) for item in cart_items.values())

    if request.method == 'POST':
        # Capture the current time
        payment_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("Payment Time:", payment_time)
        # Store the payment time in the session or database
        session['payment_time'] = payment_time

        # Process the form submission
        shipping_address = request.form['U_SA']
        postal = request.form['U_P']
        unit_no = request.form['U_UN']
        card_number = request.form['U_CNO']
        expiry_date = request.form['U_ED']
        cvc = request.form['U_CVC']
        card_name = request.form['U_CN']

        total_price_formatted = '{:.2f}'.format(total_price)

        # Store the total price in the session
        session['total_price'] = total_price_formatted
        print("Total Price stored in session:", session['total_price'])  # Debug output

        with shelve.open('customer.db') as db:
            # Add the customer data to the database
            db['customer'] = {
                'shipping_address': shipping_address,
                'postal_code': postal,
                'unit_number': unit_no,
                'card_number': card_number,
                'expiry_date': expiry_date,
                'cvc': cvc,
                'card_name': card_name,
                'total_price': total_price_formatted,
                'payment_time': payment_time
            }

        # Redirect to the receipt route with total_price as a parameter in the URL
        return redirect(url_for('receipt'))

    return render_template('payment.html', cart_items=cart_items, total_price=total_price)

@app.route('/receipt', methods=['GET'])
def receipt():
    # Get payment information from the URL parameter
    total_price = session.get('total_price', '')
    print("Total Price retrieved from session:", total_price)

    # Retrieve customer data from the database
    with shelve.open('customer.db') as db:
        customer_data = db.get('customer', {})

    print("Total Price:", total_price)  # Debug output
    print("Customer Data:", customer_data)  # Debug output

    # Construct payment information string
    payment_info = "Payment successful!<br><br>" + \
                    "Shipping Address: " + customer_data.get('shipping_address', '') + "<br>" + \
                    "Postal Code: " + customer_data.get('postal_code', '') + "<br>" + \
                    "Unit Number: " + customer_data.get('unit_number', '') + "<br>" + \
                    "<br>Total Price: $" + total_price

    # Store order details in the order_details session variable
    session['order_details'] = {
        'shipping_address': customer_data.get('shipping_address', ''),
        'postal_code': customer_data.get('postal_code', ''),
        'unit_number': customer_data.get('unit_number', ''),
        'total_price': total_price,
    }

    order_id = str(uuid.uuid4())[:8]

    session['order_id'] = order_id

    # Render the receipt template with the payment information
    return render_template('receipt.html', payment_info=payment_info)

if __name__ == '__main__':
    app.run(debug=True)
