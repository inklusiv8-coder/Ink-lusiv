from flask import Flask, jsonify, request, send_from_directory, abort
from flask_cors import CORS
import json
import os
import uuid
import smtplib
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables from .env when present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Supabase integration has been removed.
# The application now uses local JSON files for products, users, orders, and bank transfers.

EMAIL_SENDER = os.getenv('EMAIL_SENDER', 'inklusiv8@gmail.com')
EMAIL_APP_PASSWORD = os.getenv('EMAIL_APP_PASSWORD', 'dzxt tugy xwhq lewd')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'giripy123@gmail.com')

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

PRODUCTS_FILE = os.path.join(DATA_DIR, 'products.json')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
ORDERS_FILE = os.path.join(DATA_DIR, 'orders.json')
BANK_TRANSFERS_FILE = os.path.join(DATA_DIR, 'bank_transfers.json')
CUSTOMER_CARE_FILE = os.path.join(DATA_DIR, 'customer_care.json')

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)


def load_json(path, default=None):
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return default
    return default


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def initialize_file(path, default):
    if not os.path.exists(path):
        save_json(path, default)


initialize_file(PRODUCTS_FILE, [])
initialize_file(USERS_FILE, [])
initialize_file(ORDERS_FILE, [])
initialize_file(BANK_TRANSFERS_FILE, [])
initialize_file(CUSTOMER_CARE_FILE, [])


def update_local_order_status(order_id, new_status):
    orders = load_json(ORDERS_FILE, []) or []
    order = next((o for o in orders if o.get('id') == order_id), None)
    if order:
        order['status'] = new_status
        save_json(ORDERS_FILE, orders)
    return order


def send_email(to_email, subject, html_content):
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = EMAIL_SENDER
        msg['To'] = to_email
        msg['Subject'] = subject

        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_APP_PASSWORD.replace(' ', ''))
        server.sendmail(EMAIL_SENDER, to_email, msg.as_string())
        server.quit()
        print(f'✅ Email sent to {to_email}')
    except Exception as e:
        print(f'❌ Failed to send email to {to_email}: {e}')


def send_welcome_email(user):
    subject = 'Welcome to ink-lusiv.!'
    html_content = f"""
    <html>
    <body style='font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;'>
        <div style='max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);'>
            <h1 style='color: #d4a574; text-align: center;'>Welcome to ink-lusiv.!</h1>
            <p style='font-size: 16px; line-height: 1.6;'>Hi {user.get('fullName', '')}!</p>
            <p style='font-size: 16px; line-height: 1.6;'>Congratulations! You have successfully registered on ink-lusiv. Your account is now active and ready to use.</p>
            <p style='font-size: 16px; line-height: 1.6;'>Your account details have been saved:</p>
            <ul style='font-size: 16px; line-height: 1.6;'>
                <li><strong>Name:</strong> {user.get('fullName', '')}</li>
                <li><strong>Email:</strong> {user.get('email', '')}</li>
                <li><strong>Phone:</strong> {user.get('phoneNumber', '')}</li>
                <li><strong>Address:</strong> {user.get('address', '')}, {user.get('city', '')} {user.get('zipCode', '')}</li>
            </ul>
            <p style='font-size: 16px; line-height: 1.6;'>You can now browse our premium watch collection and place orders. We look forward to serving you!</p>
            <p style='font-size: 16px; line-height: 1.6;'>Thank you for choosing ink-lusiv.!</p>
            <p style='font-size: 14px; line-height: 1.6; color: #888;'>Best regards,<br>The ink-lusiv. Team</p>
        </div>
    </body>
    </html>
    """
    send_email(user.get('email'), subject, html_content)

    admin_subject = f'New User Registration - {user.get("fullName", "New User")}'
    admin_html_content = f"""
    <html>
    <body style='font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;'>
        <div style='max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);'>
            <h1 style='color: #d4a574; text-align: center;'>New User Registered</h1>
            <p style='font-size: 16px; line-height: 1.6;'>Someone have register abi. Here are the details:</p>
            <ul style='font-size: 16px; line-height: 1.6;'>
                <li><strong>Name:</strong> {user.get('fullName', '')}</li>
                <li><strong>Email:</strong> {user.get('email', '')}</li>
                <li><strong>Phone:</strong> {user.get('phoneNumber', '')}</li>
                <li><strong>Address:</strong> {user.get('address', '')}, {user.get('city', '')} {user.get('zipCode', '')}</li>
                <li><strong>Registered At:</strong> {user.get('createdAt', '')}</li>
            </ul>
        </div>
    </body>
    </html>
    """
    send_email(ADMIN_EMAIL, admin_subject, admin_html_content)
    if EMAIL_SENDER.lower() != ADMIN_EMAIL.lower():
        send_email(EMAIL_SENDER, admin_subject, admin_html_content)


def send_order_pending_email(order, user_email):
    order_id = order.get('id', '')
    subject = f'New Order Pending - Order #{order_id[:8]}'
    admin_html = f"""
    <html>
    <body style='font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;'>
        <div style='max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);'>
            <h1 style='color: #d4a574; text-align: center;'>New Order Received</h1>
            <p style='font-size: 16px; line-height: 1.6;'>A new order has been placed and requires your attention.</p>
            <h2 style='color: #333;'>Order Details</h2>
            <ul style='font-size: 16px; line-height: 1.6;'>
                <li><strong>Order ID:</strong> {order_id}</li>
                <li><strong>Customer Email:</strong> {user_email}</li>
                <li><strong>Total:</strong> ${order.get('total', 0):.2f}</li>
                <li><strong>Status:</strong> Pending Review</li>
            </ul>
            <h3 style='color: #333;'>Items</h3>
            <ul style='font-size: 16px; line-height: 1.6;'>
    """
    for item in order.get('cart', []):
        admin_html += f"<li>{item.get('name', 'Item')} x {item.get('quantity', 1)} - ${item.get('price', 0):.2f}</li>"
    admin_html += f"""
            </ul>
            <p style='font-size: 16px; line-height: 1.6; margin-top: 20px;'>
                <a href='http://localhost:5000/admin/#orders' style='display: inline-block; background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;'>Review in Admin Panel</a>
            </p>
        </div>
    </body>
    </html>
    """
    send_email(ADMIN_EMAIL, subject, admin_html)
    if EMAIL_SENDER.lower() != ADMIN_EMAIL.lower():
        send_email(EMAIL_SENDER, subject, admin_html)


def send_order_confirmed_email(order, user_info):
    subject = f'Your Order is Confirmed - Order #{order.get("id", "")[:8]}'
    html_content = f"""
    <html>
    <body style='font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;'>
        <div style='max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);'>
            <h1 style='color: #d4a574; text-align: center;'>Order Confirmed!</h1>
            <p style='font-size: 16px; line-height: 1.6;'>Hi {user_info.get('fullName', 'Customer')},</p>
            <p style='font-size: 16px; line-height: 1.6;'>Great news! Your order has been confirmed by our admin team and is now being processed for shipment.</p>
            <h2 style='color: #333;'>Order Details</h2>
            <ul style='font-size: 16px; line-height: 1.6;'>
                <li><strong>Order ID:</strong> {order.get('id', '')}</li>
                <li><strong>Status:</strong> Confirmed</li>
                <li><strong>Total:</strong> ${order.get('total', 0):.2f}</li>
            </ul>
            <h3 style='color: #333;'>Items Ordered</h3>
            <ul style='font-size: 16px; line-height: 1.6;'>
    """
    for item in order.get('cart', []):
        html_content += f"<li>{item.get('name', 'Item')} x {item.get('quantity', 1)} - ${item.get('price', 0):.2f}</li>"
    html_content += """
            </ul>
            <p style='font-size: 16px; line-height: 1.6;'>Thank you for your purchase! We will notify you when your order ships.</p>
            <p style='font-size: 14px; line-height: 1.6; color: #888;'>Best regards,<br>The ink-lusiv. Team</p>
        </div>
    </body>
    </html>
    """
    send_email(user_info.get('email'), subject, html_content)


def send_order_cancelled_email(order, user_info):
    subject = f'Your Order has been Cancelled - Order #{order.get("id", "")[:8]}'
    html_content = f"""
    <html>
    <body style='font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;'>
        <div style='max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);'>
            <h1 style='color: #d4a574; text-align: center;'>Order Cancelled</h1>
            <p style='font-size: 16px; line-height: 1.6;'>Hi {user_info.get('fullName', 'Customer')},</p>
            <p style='font-size: 16px; line-height: 1.6;'>We are sorry to let you know that your order has been cancelled.</p>
            <h2 style='color: #333;'>Order Details</h2>
            <ul style='font-size: 16px; line-height: 1.6;'>
                <li><strong>Order ID:</strong> {order.get('id', '')}</li>
                <li><strong>Status:</strong> Cancelled</li>
                <li><strong>Total:</strong> ${order.get('total', 0):.2f}</li>
            </ul>
            <h3 style='color: #333;'>Items Ordered</h3>
            <ul style='font-size: 16px; line-height: 1.6;'>
    """
    for item in order.get('cart', []):
        html_content += f"<li>{item.get('name', 'Item')} x {item.get('quantity', 1)} - ${item.get('price', 0):.2f}</li>"
    html_content += """
            </ul>
            <p style='font-size: 16px; line-height: 1.6;'>If you have any questions, please reply to this email or contact our support team.</p>
            <p style='font-size: 14px; line-height: 1.6; color: #888;'>Best regards,<br>The ink-lusiv. Team</p>
        </div>
    </body>
    </html>
    """
    send_email(user_info.get('email'), subject, html_content)


def send_order_receipt_email(order, user_email, user_name='Customer'):
    order_id = order.get('id', '')
    subject = f'Order Received - Order #{order_id[:8]}'
    html_content = f"""
    <html>
    <body style='font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;'>
        <div style='max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);'>
            <h1 style='color: #d4a574; text-align: center;'>Order Received!</h1>
            <p style='font-size: 16px; line-height: 1.6;'>Hi {user_name},</p>
            <p style='font-size: 16px; line-height: 1.6;'>Thank you for placing an order with ink-lusiv.! We have received your order and our team will review it shortly.</p>
            <h2 style='color: #333;'>Your Order Details</h2>
            <ul style='font-size: 16px; line-height: 1.6;'>
                <li><strong>Order ID:</strong> {order_id}</li>
                <li><strong>Order Date:</strong> {order.get('createdAt', 'N/A')}</li>
                <li><strong>Status:</strong> Pending Review</li>
            </ul>
            <h3 style='color: #333;'>Items Ordered</h3>
            <ul style='font-size: 16px; line-height: 1.6;'>
    """
    for item in order.get('cart', []):
        html_content += f"<li>{item.get('name', 'Item')} x {item.get('quantity', 1)} - ${item.get('price', 0):.2f}</li>"
    
    subtotal = order.get('subtotal', 0)
    shipping = order.get('shipping', 0)
    tax = order.get('tax', 0)
    total = order.get('total', 0)
    
    html_content += f"""
            </ul>
            <h3 style='color: #333;'>Order Summary</h3>
            <table style='width: 100%; font-size: 16px; line-height: 1.8;'>
                <tr style='border-bottom: 1px solid #eee;'>
                    <td style='text-align: left;'><strong>Subtotal:</strong></td>
                    <td style='text-align: right;'>${subtotal:.2f}</td>
                </tr>
                <tr style='border-bottom: 1px solid #eee;'>
                    <td style='text-align: left;'><strong>Shipping:</strong></td>
                    <td style='text-align: right;'>${shipping:.2f}</td>
                </tr>
                <tr style='border-bottom: 1px solid #eee;'>
                    <td style='text-align: left;'><strong>Tax:</strong></td>
                    <td style='text-align: right;'>${tax:.2f}</td>
                </tr>
                <tr style='background-color: #f9f9f9;'>
                    <td style='text-align: left;'><strong>Total:</strong></td>
                    <td style='text-align: right; font-size: 18px; color: #d4a574;'><strong>${total:.2f}</strong></td>
                </tr>
            </table>
            <p style='font-size: 16px; line-height: 1.6; margin-top: 20px;'>Our team will review your order and send you a confirmation email once it has been approved. Thank you for choosing ink-lusiv.!</p>
            <p style='font-size: 14px; line-height: 1.6; color: #888;'>Best regards,<br>The ink-lusiv. Team</p>
        </div>
    </body>
    </html>
    """
    send_email(user_email, subject, html_content)


def send_contact_email(contact):
    user_subject = 'We received your message - ink-lusiv.'
    user_html = f"""
    <html>
    <body style='font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;'>
        <div style='max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);'>
            <h1 style='color: #d4a574; text-align: center;'>Thanks for reaching out!</h1>
            <p style='font-size: 16px; line-height: 1.6;'>Hi {contact.get('name', '')},</p>
            <p style='font-size: 16px; line-height: 1.6;'>We received your message and will reply as soon as possible.</p>
            <p style='font-size: 16px; line-height: 1.6;'>Here is what you sent:</p>
            <blockquote style='font-size: 16px; line-height: 1.6; border-left: 4px solid #d4a574; padding-left: 12px; color: #555;'>{contact.get('message', '')}</blockquote>
            <p style='font-size: 16px; line-height: 1.6;'>Thanks for choosing ink-lusiv.!</p>
        </div>
    </body>
    </html>
    """
    admin_subject = f'New Contact Message from {contact.get("name", "Customer")}'
    admin_html = f"""
    <html>
    <body style='font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;'>
        <div style='max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);'>
            <h1 style='color: #d4a574; text-align: center;'>New Contact Message</h1>
            <p style='font-size: 16px; line-height: 1.6;'>A visitor sent a message from the site:</p>
            <ul style='font-size: 16px; line-height: 1.6;'>
                <li><strong>Name:</strong> {contact.get('name', '')}</li>
                <li><strong>Email:</strong> {contact.get('email', '')}</li>
                <li><strong>Message:</strong> {contact.get('message', '')}</li>
            </ul>
        </div>
    </body>
    </html>
    """
    send_email(contact.get('email'), user_subject, user_html)
    send_email(ADMIN_EMAIL, admin_subject, admin_html)


# Supabase helper functions removed.


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/admin/', defaults={'path': ''})
@app.route('/admin/<path:path>')
def admin_static(path):
    admin_dir = 'admin'
    if not path:
        return send_from_directory(admin_dir, 'index.html')

    if os.path.isdir(os.path.join(admin_dir, path)):
        return send_from_directory(admin_dir, os.path.join(path, 'index.html'))

    file_path = os.path.join(admin_dir, path)
    if os.path.exists(file_path):
        return send_from_directory(admin_dir, path)

    abort(404)


@app.route('/api/products', methods=['GET'])
def get_products():
    category = request.args.get('category', 'all').strip().lower()
    products = load_json(PRODUCTS_FILE, [])
    if category != 'all':
        products = [product for product in products if str(product.get('category', '')).lower() == category]
    return jsonify(products)


@app.route('/api/products', methods=['POST'])
def create_product():
    payload = request.get_json() or {}
    name = payload.get('name', '').strip()
    category = payload.get('category', '').strip()
    price = payload.get('price')
    stock = payload.get('stock', 0)

    if not name or not category or price is None:
        return jsonify({'error': 'Name, category, and price are required.'}), 400

    products = load_json(PRODUCTS_FILE, [])
    new_product = {
        'id': str(uuid.uuid4()),
        'name': name,
        'category': category,
        'price': float(price),
        'originalPrice': float(payload.get('originalPrice', price)) if payload.get('originalPrice') else float(price),
        'rating': float(payload.get('rating', 0)) if payload.get('rating') else 0,
        'reviews': int(payload.get('reviews', 0)) if payload.get('reviews') else 0,
        'stock': int(stock) if stock is not None else 0,
        'image': payload.get('image', '').strip(),
        'description': payload.get('description', '').strip(),
        'status': payload.get('status', 'available'),
        'specs': payload.get('specs', {}),
        'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    }
    products.append(new_product)
    save_json(PRODUCTS_FILE, products)
    return jsonify(new_product), 201


@app.route('/api/products/<product_id>', methods=['PUT'])
def update_product(product_id):
    payload = request.get_json() or {}
    products = load_json(PRODUCTS_FILE, [])
    product = next((p for p in products if p.get('id') == product_id), None)
    if not product:
        return jsonify({'error': 'Product not found.'}), 404

    if 'name' in payload:
        product['name'] = payload.get('name', '').strip()
    if 'category' in payload:
        product['category'] = payload.get('category', '').strip()
    if 'price' in payload:
        product['price'] = float(payload.get('price', product.get('price', 0)))
    if 'originalPrice' in payload:
        product['originalPrice'] = float(payload.get('originalPrice', product.get('price', 0)))
    if 'rating' in payload:
        product['rating'] = float(payload.get('rating', product.get('rating', 0)))
    if 'reviews' in payload:
        product['reviews'] = int(payload.get('reviews', product.get('reviews', 0)))
    if 'stock' in payload:
        product['stock'] = int(payload.get('stock', product.get('stock', 0)))
    if 'image' in payload:
        product['image'] = payload.get('image', '').strip()
    if 'description' in payload:
        product['description'] = payload.get('description', '').strip()
    if 'status' in payload:
        product['status'] = payload.get('status', product.get('status', 'available'))
    if 'specs' in payload:
        product['specs'] = payload.get('specs', product.get('specs', {}))

    save_json(PRODUCTS_FILE, products)
    return jsonify(product)


@app.route('/api/register', methods=['POST'])
def register():
    payload = request.get_json() or {}
    email = payload.get('email', '').strip().lower()
    password = payload.get('password', '')
    confirm_password = payload.get('confirmPassword', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400

    if password != confirm_password:
        return jsonify({'error': 'Passwords do not match.'}), 400

    users = load_json(USERS_FILE, [])
    if any(user['email'] == email for user in users):
        return jsonify({'error': 'Email is already registered.'}), 400

    new_user = {
        'id': str(uuid.uuid4()),
        'fullName': payload.get('fullName', '').strip(),
        'email': email,
        'phoneNumber': payload.get('phoneNumber', '').strip(),
        'address': payload.get('address', '').strip(),
        'city': payload.get('city', '').strip(),
        'zipCode': payload.get('zipCode', '').strip(),
        'password': password,
        'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    }

    users.append(new_user)
    save_json(USERS_FILE, users)

    # Send welcome and admin notification emails for new registrations
    send_welcome_email(new_user)
    sanitized_user = {k: v for k, v in new_user.items() if k != 'password'}
    return jsonify({'user': sanitized_user}), 201


@app.route('/api/login', methods=['POST'])
def login():
    payload = request.get_json() or {}
    email = payload.get('email', '').strip().lower()
    password = payload.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400

    users = load_json(USERS_FILE, [])
    user = next((user for user in users if user['email'] == email and user['password'] == password), None)

    if not user:
        return jsonify({'error': 'Invalid email or password.'}), 401

    sanitized_user = {k: v for k, v in user.items() if k != 'password'}
    return jsonify({'user': sanitized_user})


@app.route('/api/orders', methods=['POST'])
def create_order():
    payload = request.get_json() or {}
    cart = payload.get('cart', [])
    billing = payload.get('billing', {})
    payment_method = payload.get('paymentMethod', 'card')

    if not isinstance(cart, list) or len(cart) == 0:
        return jsonify({'error': 'Cart cannot be empty.'}), 400

    subtotal = sum(item.get('price', 0) * item.get('quantity', 1) for item in cart)
    shipping = 1000 if subtotal > 0 else 0
    tax = round(subtotal * 0.08, 2)
    total = round(subtotal + shipping + tax, 2)

    order = {
        'id': str(uuid.uuid4()),
        'cart': cart,
        'billing': billing,
        'paymentMethod': payment_method,
        'status': 'pending',
        'subtotal': subtotal,
        'shipping': shipping,
        'tax': tax,
        'total': total,
        'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    }

    orders = load_json(ORDERS_FILE, [])
    orders.append(order)
    save_json(ORDERS_FILE, orders)

    user_email = billing.get('email', '')
    if user_email:
        user_name = billing.get('firstName', '') or billing.get('fullName', 'Customer')
        send_order_receipt_email(order, user_email, user_name)
        send_order_pending_email(order, user_email)

    return jsonify({'order': order}), 201


@app.route('/api/contact', methods=['POST'])
def submit_contact_message():
    payload = request.get_json() or {}
    name = payload.get('name', '').strip()
    email = payload.get('email', '').strip()
    message = payload.get('message', '').strip()

    if not name or not email or not message:
        return jsonify({'error': 'Name, email, and message are required.'}), 400

    contact = {
        'name': name,
        'email': email,
        'message': message,
        'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    }

    send_contact_email(contact)
    return jsonify({'message': 'Contact message sent successfully.'}), 200



@app.route('/api/orders', methods=['GET'])
def get_orders():
    print('GET /api/orders called')
    local_orders = load_json(ORDERS_FILE, []) or []
    return jsonify({'orders': local_orders})


@app.route('/api/orders/confirmed', methods=['GET'])
def get_confirmed_orders():
    local_orders = [o for o in load_json(ORDERS_FILE, []) or [] if o.get('status') == 'confirmed']
    return jsonify({'orders': local_orders})


@app.route('/api/orders/cancelled', methods=['GET'])
def get_cancelled_orders():
    local_orders = [o for o in load_json(ORDERS_FILE, []) or [] if o.get('status') == 'cancelled']
    return jsonify({'orders': local_orders})


@app.route('/api/orders/<order_id>', methods=['PUT'])
def update_order(order_id):
    payload = request.get_json() or {}
    new_status = payload.get('status')

    if not new_status:
        return jsonify({'error': 'Status is required.'}), 400

    updated_order = update_local_order_status(order_id, new_status)
    if not updated_order:
        return jsonify({'error': 'Order not found.'}), 404

    if new_status.lower() in {'confirmed', 'accepted'}:
        billing = updated_order.get('billing', {}) or {}
        user_email = billing.get('email')
        if user_email:
            users = load_json(USERS_FILE, []) or []
            user = next((u for u in users if u.get('email', '').lower() == user_email.lower()), None)
            if not user:
                user = {
                    'fullName': f"{billing.get('firstName', '').strip()} {billing.get('lastName', '').strip()}".strip() or billing.get('name', 'Customer'),
                    'email': user_email
                }
            try:
                send_order_confirmed_email(updated_order, user)
            except Exception as e:
                print('Order confirmation email error:', e)
    elif new_status.lower() == 'cancelled':
        billing = updated_order.get('billing', {}) or {}
        user_email = billing.get('email')
        if user_email:
            users = load_json(USERS_FILE, []) or []
            user = next((u for u in users if u.get('email', '').lower() == user_email.lower()), None)
            if not user:
                user = {
                    'fullName': f"{billing.get('firstName', '').strip()} {billing.get('lastName', '').strip()}".strip() or billing.get('name', 'Customer'),
                    'email': user_email
                }
            try:
                send_order_cancelled_email(updated_order, user)
            except Exception as e:
                print('Order cancellation email error:', e)

    return jsonify({'order': updated_order})


@app.route('/api/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    orders = load_json(ORDERS_FILE, [])
    order = next((order for order in orders if order['id'] == order_id), None)
    if not order:
        return jsonify({'error': 'Order not found.'}), 404
    return jsonify({'order': order})


@app.route('/api/bank-transfers', methods=['POST'])
def create_bank_transfer():
    payload = request.get_json() or {}
    cart = payload.get('cart', [])
    billing = payload.get('billing', {})

    if not isinstance(cart, list) or len(cart) == 0:
        return jsonify({'error': 'Cart cannot be empty.'}), 400

    subtotal = sum(item.get('price', 0) * item.get('quantity', 1) for item in cart)
    shipping = 1000 if subtotal > 0 else 0
    tax = round(subtotal * 0.08, 2)
    total = round(subtotal + shipping + tax, 2)

    transfer = {
        'id': str(uuid.uuid4()),
        'cart': cart,
        'billing': billing,
        'status': 'pending',
        'subtotal': subtotal,
        'shipping': shipping,
        'tax': tax,
        'total': total,
        'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    }

    transfers = load_json(BANK_TRANSFERS_FILE, [])
    transfers.append(transfer)
    save_json(BANK_TRANSFERS_FILE, transfers)
    return jsonify({'transfer': transfer}), 201


@app.route('/api/bank-transfers', methods=['GET'])
def get_bank_transfers():
    transfers = load_json(BANK_TRANSFERS_FILE, []) or []
    return jsonify({'transfers': transfers})


@app.route('/api/bank-transfers/<transfer_id>', methods=['PUT'])
def update_bank_transfer(transfer_id):
    payload = request.get_json() or {}
    new_status = payload.get('status')

    if not new_status:
        return jsonify({'error': 'Status is required.'}), 400

    transfers = load_json(BANK_TRANSFERS_FILE, []) or []
    transfer = next((t for t in transfers if t.get('id') == transfer_id), None)
    if not transfer:
        return jsonify({'error': 'Bank transfer not found.'}), 404

    transfer['status'] = new_status
    save_json(BANK_TRANSFERS_FILE, transfers)
    return jsonify({'transfer': transfer})


@app.route('/<path:path>')
def static_proxy(path):
    if path.startswith('api/'):
        abort(404)

    if os.path.isdir(path):
        index_path = os.path.join(path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory('.', index_path)

    if os.path.exists(path):
        return send_from_directory('.', path)
    return send_from_directory('.', 'index.html')


if __name__ == '__main__':
    app.run(debug=True)
