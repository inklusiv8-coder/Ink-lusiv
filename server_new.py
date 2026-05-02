"""
E-commerce server using local JSON storage.
Organized and well-structured Flask application for managing products, orders, and bank transfers.
"""

from flask import Flask, jsonify, request, send_from_directory, abort
from flask_cors import CORS
import json
import os
import uuid
from datetime import datetime, timezone
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# =============================================================================
# CONFIGURATION AND SETUP
# =============================================================================

# Load environment variables from .env when present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Supabase integration has been removed.
# This server now uses local JSON files for products, users, orders, and bank transfers.

# File system setup
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Data file paths
PRODUCTS_FILE = os.path.join(DATA_DIR, 'products.json')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
ORDERS_FILE = os.path.join(DATA_DIR, 'orders.json')
BANK_TRANSFERS_FILE = os.path.join(DATA_DIR, 'bank_transfers.json')

# Email configuration
EMAIL_SENDER = 'inklusiv8@gmail.com'
EMAIL_APP_PASSWORD = 'dzxt tugy xwhq lewd'
ADMIN_EMAIL = 'giripy123@gmail.com'

# Flask application setup
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def load_json(path, default=None):
    """Load JSON data from file with error handling."""
    if default is None:
        default = {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"⚠️  Could not load {path}: {e}")
        return default


def save_json(path, data):
    """Save data to JSON file with pretty formatting."""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Could not save to {path}: {e}")


def initialize_data_files():
    """Initialize data files with empty arrays if they don't exist."""
    data_files = [
        (PRODUCTS_FILE, []),
        (USERS_FILE, []),
        (ORDERS_FILE, []),
        (BANK_TRANSFERS_FILE, [])
    ]

    for file_path, default_data in data_files:
        if not os.path.exists(file_path):
            save_json(file_path, default_data)
            print(f"📄 Initialized {os.path.basename(file_path)}")

# Initialize data files
initialize_data_files()


# =============================================================================
# EMAIL FUNCTIONS
# =============================================================================

def send_email(to_email, subject, html_content):
    """Send an email using Gmail SMTP."""
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
        print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")


def send_welcome_email(user):
    """Send a welcome email to a new user."""
    subject = "Welcome to ink-lusiv.!"
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
            <h1 style="color: #d4a574; text-align: center;">Welcome to ink-lusiv.!</h1>
            <p style="font-size: 16px; line-height: 1.6;">Dear {user['fullName']},</p>
            <p style="font-size: 16px; line-height: 1.6;">Thank you for registering with ink-lusiv.! We're excited to have you as part of our community.</p>
            <p style="font-size: 16px; line-height: 1.6;">Your account has been successfully created with the following details:</p>
            <ul style="font-size: 16px; line-height: 1.6;">
                <li><strong>Name:</strong> {user['fullName']}</li>
                <li><strong>Email:</strong> {user['email']}</li>
                <li><strong>Phone:</strong> {user['phoneNumber']}</li>
                <li><strong>Address:</strong> {user['address']}, {user['city']}, {user['zipCode']}</li>
            </ul>
            <p style="font-size: 16px; line-height: 1.6;">You can now browse our collection of premium watches and place orders.</p>
            <p style="font-size: 16px; line-height: 1.6;">Best regards,<br>The ink-lusiv. Team</p>
        </div>
    </body>
    </html>
    """
    send_email(user['email'], subject, html_content)

    # Send notification to admins
    admin_subject = f"New User Registration - {user['fullName']}"
    admin_html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
            <h1 style="color: #d4a574; text-align: center;">New User Registration</h1>
            <p style="font-size: 16px; line-height: 1.6;">A new user has registered on ink-lusiv.!</p>
            <h2 style="color: #333;">User Details:</h2>
            <ul style="font-size: 16px; line-height: 1.6;">
                <li><strong>Name:</strong> {user['fullName']}</li>
                <li><strong>Email:</strong> {user['email']}</li>
                <li><strong>Phone:</strong> {user['phoneNumber']}</li>
                <li><strong>Address:</strong> {user['address']}, {user['city']}, {user['zipCode']}</li>
                <li><strong>Registered At:</strong> {user['createdAt']}</li>
            </ul>
            <p style="font-size: 16px; line-height: 1.6;">Please review the registration in the admin panel.</p>
        </div>
    </body>
    </html>
    """
    send_email(EMAIL_SENDER, admin_subject, admin_html_content)
    send_email(ADMIN_EMAIL, admin_subject, admin_html_content)


def send_order_confirmation_email(order, user_info):
    """Send order confirmation email to user and admin."""
    subject = f"Order Confirmation - Order #{order['id'][:8]}"
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
            <h1 style="color: #d4a574; text-align: center;">Order Confirmed!</h1>
            <p style="font-size: 16px; line-height: 1.6;">Dear {user_info.get('fullName', 'Customer')},</p>
            <p style="font-size: 16px; line-height: 1.6;">Your order has been accepted and is now being processed.</p>
            <h2 style="color: #333;">Order Details:</h2>
            <ul style="font-size: 16px; line-height: 1.6;">
                <li><strong>Order ID:</strong> {order['id']}</li>
                <li><strong>Status:</strong> {order['status']}</li>
                <li><strong>Total:</strong> ${order['total']:.2f}</li>
            </ul>
            <h3 style="color: #333;">Items:</h3>
            <ul style="font-size: 16px; line-height: 1.6;">
    """
    for item in order['cart']:
        html_content += f"<li>{item['name']} x {item['quantity']} - ${item['price']:.2f} each</li>"
    html_content += f"""
            </ul>
            <p style="font-size: 16px; line-height: 1.6;">Thank you for shopping with ink-lusiv.!</p>
            <p style="font-size: 16px; line-height: 1.6;">Best regards,<br>The ink-lusiv. Team</p>
        </div>
    </body>
    </html>
    """
    send_email(user_info['email'], subject, html_content)
    # Also send to admin
    send_email(ADMIN_EMAIL, f"New Order Accepted - {order['id'][:8]}", html_content)


# Supabase integration has been removed from this file.
# The server now uses local JSON files for all data storage and retrieval.


# =============================================================================
# FLASK ROUTES - STATIC FILES
# =============================================================================

@app.route('/')
def index():
    """Serve the main index page."""
    return send_from_directory('.', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files and handle directory routes like /admin/."""
    # Support directory routes like /admin/ by serving index.html from that folder.
    if os.path.isdir(path):
        index_path = os.path.join(path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory('.', index_path)

    if os.path.exists(path):
        return send_from_directory('.', path)
    return send_from_directory('.', 'index.html')

# =============================================================================
# FLASK ROUTES - API ENDPOINTS
# =============================================================================

# PRODUCTS API
@app.route('/api/products', methods=['GET'])
def get_products():
    """Get products, optionally filtered by category."""
    category = request.args.get('category', 'all')
    products = load_json(PRODUCTS_FILE, []) or []
    if category and category.lower() != 'all':
        products = [product for product in products if str(product.get('category', '')).lower() == category.lower()]
    return jsonify({'products': products})

# USERS API
@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user."""
    user = request.get_json() or {}
    required_fields = ['fullName', 'email', 'phoneNumber', 'address', 'city', 'zipCode']

    if not all(field in user for field in required_fields):
        return jsonify({'error': 'Missing required fields.'}), 400

    user['id'] = str(uuid.uuid4())
    user['createdAt'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    try:
        users = load_json(USERS_FILE, [])
        existing_user = next((u for u in users if u['email'] == user['email']), None)
        
        if existing_user:
            # Update existing user
            existing_user.update(user)
            user = existing_user
        else:
            # Create new user
            users.append(user)

        save_json(USERS_FILE, users)

        # Verify the user was actually saved
        saved_users = load_json(USERS_FILE, [])
        saved_user = next((u for u in saved_users if u['email'] == user['email']), None)
        if not saved_user:
            return jsonify({'error': 'Failed to save user data.'}), 500

        # Only send email if user was successfully saved and is new
        if not existing_user:
            send_welcome_email(user)

        return jsonify({'user': user}), 201

    except Exception as e:
        print(f'Error saving user: {e}')
        return jsonify({'error': 'Failed to save user data.'}), 500


@app.route('/api/register', methods=['POST'])
def register_alias():
    return create_user()


# ORDERS API
@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create a new order."""
    payload = request.get_json() or {}
    cart = payload.get('cart', [])
    billing = payload.get('billing', {})
    payment_method = payload.get('paymentMethod', 'card')

    if not isinstance(cart, list) or len(cart) == 0:
        return jsonify({'error': 'Cart cannot be empty.'}), 400

    # Calculate totals
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

    return jsonify({'order': order}), 201


@app.route('/api/orders', methods=['GET'])
def get_orders():
    """Get all orders."""
    print('📋 GET /api/orders called')
    orders = load_json(ORDERS_FILE, []) or []
    return jsonify({'orders': orders})


@app.route('/api/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    """Get a specific order by ID."""
    orders = load_json(ORDERS_FILE, [])
    order = next((order for order in orders if order['id'] == order_id), None)
    if not order:
        return jsonify({'error': 'Order not found.'}), 404
    return jsonify({'order': order})


@app.route('/api/orders/<order_id>', methods=['PUT'])
def update_order(order_id):
    """Update an order's status."""
    payload = request.get_json() or {}
    new_status = payload.get('status')

    if not new_status:
        return jsonify({'error': 'Status is required.'}), 400

    orders = load_json(ORDERS_FILE, [])
    order = next((o for o in orders if o['id'] == order_id), None)
    if not order:
        return jsonify({'error': 'Order not found.'}), 404

    order['status'] = new_status
    save_json(ORDERS_FILE, orders)

    # Send confirmation email if order is accepted
    if new_status.lower() == 'accepted':
        # Find user by email from billing
        billing = order.get('billing', {})
        user_email = billing.get('email')
        if user_email:
            users = load_json(USERS_FILE, [])
            user = next((u for u in users if u['email'] == user_email), None)
            if not user:
                # Use billing info as user
                user = {
                    'fullName': billing.get('firstName', '') + ' ' + billing.get('lastName', ''),
                    'email': user_email
                }
            send_order_confirmation_email(order, user)

    return jsonify({'order': order})

# BANK TRANSFERS API
@app.route('/api/bank-transfers', methods=['POST'])
def create_bank_transfer():
    """Create a new bank transfer."""
    payload = request.get_json() or {}
    cart = payload.get('cart', [])
    billing = payload.get('billing', {})

    if not isinstance(cart, list) or len(cart) == 0:
        return jsonify({'error': 'Cart cannot be empty.'}), 400

    # Calculate totals
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
    """Get all bank transfers."""
    print('🏦 GET /api/bank-transfers called')
    transfers = load_json(BANK_TRANSFERS_FILE, []) or []
    return jsonify({'transfers': transfers})


@app.route('/api/bank-transfers/<transfer_id>', methods=['PUT'])
def update_bank_transfer(transfer_id):
    """Update a bank transfer's status."""
    payload = request.get_json() or {}
    new_status = payload.get('status')

    if not new_status:
        return jsonify({'error': 'Status is required.'}), 400

    transfers = load_json(BANK_TRANSFERS_FILE, [])
    transfer = next((t for t in transfers if t['id'] == transfer_id), None)
    if not transfer:
        return jsonify({'error': 'Bank transfer not found.'}), 404

    transfer['status'] = new_status
    save_json(BANK_TRANSFERS_FILE, transfers)

    return jsonify({'transfer': transfer})

# =============================================================================
# APPLICATION ENTRY POINT
# =============================================================================

if __name__ == '__main__':
    print('🚀 Starting E-commerce Server...')
    print(' Using local JSON files only')
    print('🌐 Server will be available at http://127.0.0.1:5000')
    app.run(debug=True)