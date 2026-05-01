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

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
SUPABASE_PUBLIC_KEY = os.getenv('SUPABASE_KEY')
supabase = None
supabase_is_service_role = False

if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
    try:
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        supabase_is_service_role = True
        print(f"Supabase client initialized: {SUPABASE_URL}")
        print('Using SUPABASE_SERVICE_ROLE_KEY for backend sync.')
    except Exception as e:
        print('Could not initialize Supabase client with service role key:', e)
        supabase = None
elif SUPABASE_URL and SUPABASE_PUBLIC_KEY:
    try:
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_PUBLIC_KEY)
        print(f"Supabase client initialized: {SUPABASE_URL}")
        print('Using SUPABASE_KEY for readonly Supabase access only. Backend writes are disabled.')
    except Exception as e:
        print('Could not initialize Supabase client with public key:', e)
        supabase = None
else:
    if not SUPABASE_URL:
        print('SUPABASE_URL is missing. Set it in your environment or .env file.')
    if not SUPABASE_SERVICE_ROLE_KEY and not SUPABASE_PUBLIC_KEY:
        print('Supabase key is missing. Set SUPABASE_SERVICE_ROLE_KEY for server-side inserts or SUPABASE_KEY for readonly access.')
    elif not SUPABASE_SERVICE_ROLE_KEY:
        print('Supabase service role key is missing. Server-side inserts and sync are disabled.')
    print('Supabase user/order sync will be disabled.')

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


def sync_supabase_user(user):
    if not supabase or not supabase_is_service_role:
        return
    try:
        supabase.table('users').insert({
            'id': user['id'],
            'full_name': user['fullName'],
            'email': user['email'],
            'phone_number': user['phoneNumber'],
            'address': user['address'],
            'city': user['city'],
            'zip_code': user['zipCode'],
            'created_at': user['createdAt']
        }).execute()
        print(f'✅ User {user.get("email")} synced to Supabase')
    except Exception:
        pass  # Silently fail - local JSON storage is primary


def sync_supabase_order(order):
    if not supabase or not supabase_is_service_role:
        print('Supabase service role client missing: cannot sync order')
        return
    try:
        response = supabase.table('orders').insert({
            'id': order['id'],
            'cart': order['cart'],
            'billing': order['billing'],
            'payment_method': order['paymentMethod'],
            'status': order['status'],
            'subtotal': order['subtotal'],
            'shipping': order['shipping'],
            'tax': order['tax'],
            'total': order['total'],
            'created_at': order['createdAt']
        }).execute()
        if getattr(response, 'error', None):
            print('Supabase order sync error:', response.error)
        else:
            print('Supabase order synced:', getattr(response, 'data', response))
    except Exception as e:
        print('Supabase order sync exception:', e)


def delete_supabase_order_from_table(order_id, table_name):
    try:
        response = supabase.table(table_name).delete().eq('id', order_id).execute()
        if getattr(response, 'error', None):
            print(f'Supabase delete from {table_name} error:', response.error)
    except Exception as e:
        print(f'Supabase delete from {table_name} exception:', e)


def sync_supabase_order_status_table(order, table_name):
    if not supabase or not supabase_is_service_role:
        print(f'Supabase service role client missing: cannot sync order to {table_name}')
        return
    try:
        response = supabase.table(table_name).upsert({
            'id': order['id'],
            'cart': order.get('cart', []),
            'billing': order.get('billing', {}),
            'payment_method': order.get('paymentMethod'),
            'status': order.get('status'),
            'subtotal': order.get('subtotal', 0),
            'shipping': order.get('shipping', 0),
            'tax': order.get('tax', 0),
            'total': order.get('total', 0),
            'created_at': order.get('createdAt')
        }).execute()
        if getattr(response, 'error', None):
            print(f'Supabase {table_name} sync error:', response.error)
        else:
            print(f'Supabase {table_name} synced:', getattr(response, 'data', response))
    except Exception as e:
        print(f'Supabase {table_name} sync exception:', e)


def sync_supabase_confirmed_order(order):
    if supabase and supabase_is_service_role:
        delete_supabase_order_from_table(order['id'], 'cancelled_orders')
    sync_supabase_order_status_table(order, 'confirmed_orders')


def sync_supabase_cancelled_order(order):
    if supabase and supabase_is_service_role:
        delete_supabase_order_from_table(order['id'], 'confirmed_orders')
    sync_supabase_order_status_table(order, 'cancelled_orders')


def sync_supabase_bank_transfer(transfer):
    if not supabase or not supabase_is_service_role:
        print('Supabase service role client missing: cannot sync bank transfer')
        return
    try:
        response = supabase.table('bank_transfers').insert({
            'id': transfer['id'],
            'cart': transfer['cart'],
            'billing': transfer['billing'],
            'status': transfer['status'],
            'subtotal': transfer['subtotal'],
            'shipping': transfer['shipping'],
            'tax': transfer['tax'],
            'total': transfer['total'],
            'created_at': transfer['createdAt']
        }).execute()
        if getattr(response, 'error', None):
            print('Supabase bank transfer sync error:', response.error)
        else:
            print('Supabase bank transfer synced:', getattr(response, 'data', response))
    except Exception as e:
        print('Supabase bank transfer sync exception:', e)


def normalize_supabase_product(record):
    if not isinstance(record, dict):
        return record

    normalized = dict(record)
    if 'original_price' in normalized:
        normalized['originalPrice'] = normalized.pop('original_price')
    if 'created_at' in normalized:
        normalized['createdAt'] = normalized.pop('created_at')
    return normalized


def normalize_supabase_order(record):
    if not isinstance(record, dict):
        return record

    normalized = dict(record)
    if 'payment_method' in normalized:
        normalized['paymentMethod'] = normalized.pop('payment_method')
    if 'created_at' in normalized:
        normalized['createdAt'] = normalized.pop('created_at')
    return normalized


def normalize_supabase_user(record):
    if not isinstance(record, dict):
        return record

    normalized = dict(record)
    if 'full_name' in normalized:
        normalized['fullName'] = normalized.pop('full_name')
    if 'phone_number' in normalized:
        normalized['phoneNumber'] = normalized.pop('phone_number')
    if 'zip_code' in normalized:
        normalized['zipCode'] = normalized.pop('zip_code')
    if 'created_at' in normalized:
        normalized['createdAt'] = normalized.pop('created_at')
    return normalized


def normalize_supabase_customer_care(record):
    if not isinstance(record, dict):
        return record

    normalized = dict(record)
    if 'customer_name' in normalized:
        normalized['customerName'] = normalized.pop('customer_name')
    if 'customer_email' in normalized:
        normalized['customerEmail'] = normalized.pop('customer_email')
    if 'customer_phone' in normalized:
        normalized['customerPhone'] = normalized.pop('customer_phone')
    if 'whatsapp_number' in normalized:
        normalized['whatsappNumber'] = normalized.pop('whatsapp_number')
    if 'created_at' in normalized:
        normalized['createdAt'] = normalized.pop('created_at')
    return normalized


def save_local_customer_care_entry(entry):
    messages = load_json(CUSTOMER_CARE_FILE, []) or []
    messages.append(entry)
    save_json(CUSTOMER_CARE_FILE, messages)


def normalize_customer_care_thread(thread):
    if not isinstance(thread.get('messages'), list):
        legacy_message = thread.pop('message', None)
        thread['messages'] = []
        if legacy_message:
            thread['messages'].append({
                'id': uuid.uuid4().hex,
                'sender': 'customer',
                'text': legacy_message,
                'timestamp': thread.get('createdAt') or datetime.now(timezone.utc).isoformat()
            })
    return thread


def fetch_supabase_customer_care():
    if not supabase:
        return None

    try:
        response = supabase.table('customer_service').select('*').order('created_at', desc=False).execute()
        response_error = getattr(response, 'error', None) or (response.get('error') if isinstance(response, dict) else None)
        response_data = getattr(response, 'data', None) or (response.get('data') if isinstance(response, dict) else None)

        if response_error:
            print('Supabase customer care fetch error:', response_error)
            return None

        return [normalize_supabase_customer_care(row) for row in (response_data or [])]
    except Exception as e:
        print('Supabase customer care fetch exception:', e)
        return None


def fetch_supabase_users():
    if not supabase:
        return None

    try:
        response = supabase.table('users').select('*').execute()
        response_error = getattr(response, 'error', None) or (response.get('error') if isinstance(response, dict) else None)
        response_data = getattr(response, 'data', None) or (response.get('data') if isinstance(response, dict) else None)

        if response_error:
            print('Supabase users fetch error:', response_error)
            return None

        return [normalize_supabase_user(row) for row in (response_data or [])]
    except Exception as e:
        print('Supabase users fetch exception:', e)
        return None


@app.route('/api/users', methods=['GET'])
def get_users():
    if supabase:
        users = fetch_supabase_users()
        if users is not None:
            return jsonify({'users': users})

    local_users = load_json(USERS_FILE, []) or []
    return jsonify({'users': local_users})


@app.route('/api/customer-service', methods=['GET'])
def get_customer_service_entries():
    supabase_entries = fetch_supabase_customer_care()
    if supabase_entries is not None:
        return jsonify({'entries': supabase_entries})
    return jsonify({'entries': []})


@app.route('/api/customer-care', methods=['GET', 'POST'])
def customer_care():
    if request.method == 'GET':
        try:
            local_threads = load_json(CUSTOMER_CARE_FILE, []) or []
            local_threads = [normalize_customer_care_thread(thread) for thread in local_threads]
            save_json(CUSTOMER_CARE_FILE, local_threads)
            supabase_threads = fetch_supabase_customer_care() or []
            return jsonify({
                'threads': local_threads,
                'messages': local_threads,
                'supabaseMessages': supabase_threads
            })
        except Exception as e:
            print(f'[CUSTOMER CARE GET] Error: {e}')
            return jsonify({'error': str(e)}), 500

    try:
        data = request.get_json(silent=True) or {}
        customer_name = data.get('customerName') or data.get('customer_name') or 'Anonymous'
        customer_email = data.get('customerEmail') or data.get('customer_email') or ''
        customer_phone = data.get('customerPhone') or data.get('customer_phone') or ''
        whatsapp_number = data.get('whatsappNumber') or data.get('whatsapp_number') or '9138154963'
        message = data.get('message') or data.get('text') or ''

        if not message:
            return jsonify({'error': 'Message is required'}), 400

        threads = load_json(CUSTOMER_CARE_FILE, []) or []
        
        # Find or create conversation thread
        thread = None
        if customer_email:
            thread = next((t for t in threads if t.get('customerEmail') == customer_email), None)
        elif customer_phone:
            thread = next((t for t in threads if t.get('customerPhone') == customer_phone), None)
        
        if not thread:
            thread = {
                'id': uuid.uuid4().hex,
                'customerName': customer_name,
                'customerEmail': customer_email,
                'customerPhone': customer_phone,
                'whatsappNumber': whatsapp_number,
                'messages': [],
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat()
            }
            threads.append(thread)
        else:
            # Normalize legacy records that stored a single `message` field instead of a `messages` list
            if not isinstance(thread.get('messages'), list):
                legacy_message = thread.pop('message', None)
                thread['messages'] = []
                if legacy_message:
                    thread['messages'].append({
                        'id': uuid.uuid4().hex,
                        'sender': 'customer',
                        'text': legacy_message,
                        'timestamp': thread.get('createdAt') or datetime.now(timezone.utc).isoformat()
                    })

        # Add message to thread
        thread.setdefault('messages', [])
        thread['messages'].append({
            'id': uuid.uuid4().hex,
            'sender': 'customer',
            'text': message,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        thread['updatedAt'] = datetime.now(timezone.utc).isoformat()
        
        save_json(CUSTOMER_CARE_FILE, threads)
        
        # Also sync to Supabase if available
        if supabase and supabase_is_service_role:
            try:
                insert_payload = [{
                    'name': customer_name,
                    'email': customer_email,
                    'phone': customer_phone,
                    'whatsapp': whatsapp_number,
                    'message': message,
                    'created_at': datetime.now(timezone.utc).isoformat()
                }]
                print(f'[CUSTOMER SERVICE] Syncing to Supabase: {insert_payload}')
                response = supabase.table('customer_service').insert(insert_payload).execute()
                response_error = getattr(response, 'error', None) or (response.get('error') if isinstance(response, dict) else None)
                if response_error:
                    print(f'[CUSTOMER SERVICE] Supabase sync error: {response_error}')
            except Exception as e:
                print(f'[CUSTOMER SERVICE] Supabase sync exception: {e}')

        return jsonify(thread)
    except Exception as e:
        print(f'[CUSTOMER CARE POST] Error: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/customer-care/<thread_id>/reply', methods=['POST'])
def reply_to_customer(thread_id):
    data = request.get_json(silent=True) or {}
    reply_text = data.get('message') or data.get('text') or ''
    sender = data.get('sender', 'admin')
    
    if not reply_text:
        return jsonify({'error': 'Reply text is required'}), 400
    
    threads = load_json(CUSTOMER_CARE_FILE, []) or []
    thread = next((t for t in threads if t.get('id') == thread_id), None)
    
    if not thread:
        return jsonify({'error': 'Thread not found'}), 404
    
    thread['messages'].append({
        'id': uuid.uuid4().hex,
        'sender': sender,
        'text': reply_text,
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
    thread['updatedAt'] = datetime.now(timezone.utc).isoformat()
    
    save_json(CUSTOMER_CARE_FILE, threads)
    
    return jsonify(thread)


def get_supabase_products(category='all'):
    if not supabase:
        return None

    valid_categories = {'leather', 'metal', 'silicone'}
    if category != 'all' and category not in valid_categories:
        return None

    try:
        if category == 'all':
            all_products = []
            for table_name in ('products_leather', 'products_metal', 'products_silicone'):
                response = supabase.table(table_name).select('*').execute()
                if getattr(response, 'error', None):
                    print(f'Supabase product fetch error from {table_name}:', response.error)
                    continue
                rows = getattr(response, 'data', []) or []
                all_products.extend(normalize_supabase_product(row) for row in rows)
            return all_products

        table_name = f'products_{category}'
        response = supabase.table(table_name).select('*').execute()
        if getattr(response, 'error', None):
            print(f'Supabase product fetch error from {table_name}:', response.error)
            return []
        return [normalize_supabase_product(row) for row in (getattr(response, 'data', []) or [])]
    except Exception as e:
        print('Supabase product fetch exception:', repr(e))
        return None


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


@app.route('/api/products', methods=['GET'])
def get_products():
    category = request.args.get('category', 'all').strip().lower()

    if supabase:
        supabase_products = get_supabase_products(category)
        if supabase_products is not None:
            return jsonify(supabase_products)

    products = load_json(PRODUCTS_FILE, [])
    if category != 'all':
        products = [product for product in products if str(product.get('category', '')).lower() == category]

    return jsonify(products)


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

    try:
        sync_supabase_user(new_user)
    except Exception:
        pass
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

    try:
        sync_supabase_order(order)
    except Exception:
        pass

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


def fetch_supabase_order_table(table_name):
    if not supabase:
        return None

    try:
        response = supabase.table(table_name).select('*').execute()
        response_error = getattr(response, 'error', None) or (response.get('error') if isinstance(response, dict) else None)
        response_data = getattr(response, 'data', None) or (response.get('data') if isinstance(response, dict) else None)

        if response_error:
            print(f'Supabase {table_name} fetch error:', response_error)
            return None

        return [normalize_supabase_order(record) for record in (response_data or [])]
    except Exception as e:
        print(f'Supabase {table_name} fetch exception:', e)
        return None


@app.route('/api/orders', methods=['GET'])
def get_orders():
    print('GET /api/orders called')

    if supabase:
        try:
            print('Fetching orders from Supabase')
            response = supabase.table('orders').select('*').execute()
            response_error = getattr(response, 'error', None) or (response.get('error') if isinstance(response, dict) else None)
            response_data = getattr(response, 'data', None) or (response.get('data') if isinstance(response, dict) else None)

            if response_error:
                print('Supabase orders fetch error:', response_error)
                raise RuntimeError('Supabase fetch failed')

            if response_data is None:
                print('Supabase orders response contained no data; returning empty list')
                return jsonify({'orders': []})

            orders = [normalize_supabase_order(record) for record in (response_data or [])]
            print(f'Supabase orders: {len(orders)}')
            return jsonify({'orders': orders})
        except Exception as e:
            print('Supabase orders fetch exception:', e)
            local_orders = load_json(ORDERS_FILE, []) or []
            print(f'Returning {len(local_orders)} local orders as fallback')
            return jsonify({'orders': local_orders})

    local_orders = load_json(ORDERS_FILE, []) or []
    return jsonify({'orders': local_orders})


@app.route('/api/orders/confirmed', methods=['GET'])
def get_confirmed_orders():
    if supabase:
        confirmed = fetch_supabase_order_table('confirmed_orders')
        if confirmed is not None:
            return jsonify({'orders': confirmed})

    local_orders = [o for o in load_json(ORDERS_FILE, []) or [] if o.get('status') == 'confirmed']
    return jsonify({'orders': local_orders})


@app.route('/api/orders/cancelled', methods=['GET'])
def get_cancelled_orders():
    if supabase:
        cancelled = fetch_supabase_order_table('cancelled_orders')
        if cancelled is not None:
            return jsonify({'orders': cancelled})

    local_orders = [o for o in load_json(ORDERS_FILE, []) or [] if o.get('status') == 'cancelled']
    return jsonify({'orders': local_orders})


@app.route('/api/orders/<order_id>', methods=['PUT'])
def update_order(order_id):
    payload = request.get_json() or {}
    new_status = payload.get('status')

    if not new_status:
        return jsonify({'error': 'Status is required.'}), 400

    updated_order = None
    update_error = None

    if supabase:
        try:
            response = supabase.table('orders').update({'status': new_status}).eq('id', order_id).select('*').execute()
            response_error = getattr(response, 'error', None) or (response.get('error') if isinstance(response, dict) else None)
            response_data = getattr(response, 'data', None) or (response.get('data') if isinstance(response, dict) else None)

            if response_error:
                print('Supabase order update error:', response_error)
                update_error = 'Supabase update failed'
            else:
                updated_order = update_local_order_status(order_id, new_status)
                if response_data and len(response_data) > 0:
                    updated_order = normalize_supabase_order(response_data[0])
        except Exception as e:
            print('Supabase order update exception:', e)
            update_error = 'Supabase update exception'

    if not updated_order:
        updated_order = update_local_order_status(order_id, new_status)
        if not updated_order:
            if update_error:
                return jsonify({'error': 'Order update failed; could not find order.'}), 500
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
        sync_supabase_confirmed_order(updated_order)
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
        sync_supabase_cancelled_order(updated_order)

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

    try:
        sync_supabase_bank_transfer(transfer)
    except Exception:
        pass

    return jsonify({'transfer': transfer}), 201


@app.route('/api/bank-transfers', methods=['GET'])
def get_bank_transfers():
    print('GET /api/bank-transfers called')

    if not supabase:
        print('Supabase client not initialized; returning no bank transfers')
        return jsonify({'transfers': []})

    try:
        print('Fetching bank transfers from Supabase')
        response = supabase.table('bank_transfers').select('*').execute()
        response_error = getattr(response, 'error', None) or (response.get('error') if isinstance(response, dict) else None)
        response_data = getattr(response, 'data', None) or (response.get('data') if isinstance(response, dict) else None)

        if response_error:
            print('Supabase bank transfers fetch error:', response_error)
            return jsonify({'transfers': []})

        if response_data is None:
            print('Supabase bank transfers response contained no data; returning empty list')
            return jsonify({'transfers': []})

        transfers = response_data or []
        print(f'Supabase bank transfers: {len(transfers)}')
        return jsonify({'transfers': transfers})
    except Exception as e:
        print('Supabase bank transfers fetch exception:', e)
        return jsonify({'transfers': []})


@app.route('/api/bank-transfers/<transfer_id>', methods=['PUT'])
def update_bank_transfer(transfer_id):
    payload = request.get_json() or {}
    new_status = payload.get('status')

    if not new_status:
        return jsonify({'error': 'Status is required.'}), 400

    if not supabase:
        return jsonify({'error': 'Supabase not available.'}), 503

    try:
        # Update in Supabase
        response = supabase.table('bank_transfers').update({'status': new_status}).eq('id', transfer_id).execute()
        response_error = getattr(response, 'error', None) or (response.get('error') if isinstance(response, dict) else None)

        if response_error:
            print('Supabase bank transfer update error:', response_error)
            return jsonify({'error': 'Failed to update bank transfer in database.'}), 500

        # Return the updated transfer data
        response_data = getattr(response, 'data', None) or (response.get('data') if isinstance(response, dict) else None)
        if response_data and len(response_data) > 0:
            # Normalize if needed (assuming similar structure to orders)
            updated_transfer = response_data[0]
            return jsonify({'transfer': updated_transfer})

        return jsonify({'error': 'Bank transfer not found.'}), 404

    except Exception as e:
        print('Supabase bank transfer update exception:', e)
        return jsonify({'error': 'Database error.'}), 500


if __name__ == '__main__':
    app.run(debug=True)
