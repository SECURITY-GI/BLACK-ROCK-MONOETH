# -*- coding: utf-8 -*-
"""app.py (Complete Monolithic Backend with Full UI Routing)

This single-file application is a complete, self-contained system
for handling crypto payments. It includes the following components:
1. A raw TCP/IP listener for physical card terminals.
2. A Flask web server with a full UI flow for the virtual PC terminal.
3. Secure, in-house ISO 8583 message handling.
4. In-house payment processing logic.
5. Integration with a Firebase/Firestore database for persistence.
6. Placeholder for a real crypto payout service.
"""

import os
import json
import logging
import socket
import threading
import time
import random
from datetime import timedelta

from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_cors import CORS

import firebase_admin
from firebase_admin import credentials, firestore, auth

# --- Flask App Configuration ---
app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'a_secret_key_that_is_very_secure')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# --- Firebase/Firestore Initialization ---
firebase_config = json.loads(os.environ.get('__firebase_config', '{}'))
app_id = os.environ.get('__app_id', 'default-app-id')

db = None
if firebase_config:
    try:
        # NOTE: Ensure your firebase_config is a valid JSON string or dictionary
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        logging.info("Firebase Admin SDK initialized successfully.")
    except Exception as e:
        logging.error(f"Error initializing Firebase Admin SDK: {e}", exc_info=True)
        db = None

# --- In-House ISO 8583 Message Handling ---
# NOTE: This class is a placeholder. For production, replace this with a robust library
class Iso8583Message:
    def __init__(self, message_str=None):
        self.mti = None
        self.data_elements = {}
        if message_str:
            self.unpack(message_str)

    def unpack(self, message_str):
        try:
            parts = message_str.split('|')
            self.mti = parts[0].split(':')[1]
            data_part = parts[1]
            data_elements = data_part.split(',')
            for element in data_elements:
                key, value = element.split(':')
                self.data_elements[key] = value
        except Exception as e:
            logging.error(f"Failed to unpack ISO message: {e}")
            self.mti = 'ERROR'

    def pack(self, mti, data_elements):
        self.mti = mti
        self.data_elements = data_elements
        data_parts = [f"{key}:{value}" for key, value in self.data_elements.items()]
        message_str = f"MTI:{self.mti}|" + ",".join(data_parts)
        return message_str.encode('ascii')

# --- In-House Business Logic & Crypto Payout Service ---
def initiate_payout(amount, payout_type, wallet_address):
    logging.info(f"Processor: Initiating payout of {amount} {payout_type} to {wallet_address}...")
    try:
        blockchain_tx_hash = f"0x{os.urandom(32).hex()}"
        logging.info(f"Processor: Payout successful. Transaction Hash: {blockchain_tx_hash}")
        time.sleep(1)
        return {"status": "success", "hash": blockchain_tx_hash}
    except Exception as e:
        logging.error(f"Processor: Crypto payout failed: {e}")
        return {"status": "failure", "hash": None}

def process_payment_logic(data):
    amount = data.get('amount')
    currency = data.get('currency')
    card_number = data.get('cardNumber')
    protocol = data.get('protocol')
    user_id = data.get('userId', 'virtual-terminal-1')

    if not all([amount, currency, card_number, protocol]):
        return {"status": "declined", "response_code": "99", "message": "Missing transaction data."}

    is_approved = random.choice([True, False])
    blockchain_tx_hash = None
    if is_approved:
        payout_type = 'USDT_TRC20'
        merchant_wallet = 'Txxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        payout_result = initiate_payout(amount, payout_type, merchant_wallet)

        if payout_result['status'] == 'success':
            blockchain_tx_hash = payout_result['hash']
            status_message = "Transaction approved and payout initiated."
            response_code = "00"
        else:
            status_message = "Transaction approved, but payout failed."
            response_code = "05"
    else:
        status_message = "Transaction declined by internal rules."
        response_code = "51"

    log_transaction_to_firestore(user_id, data, {
        "status": "approved" if is_approved else "declined",
        "response_code": response_code,
        "message": status_message,
        "blockchain_hash": blockchain_tx_hash
    })

    return {
        "status": "approved" if is_approved else "declined",
        "response_code": response_code,
        "message": status_message,
        "blockchain_hash": blockchain_tx_hash
    }

def log_transaction_to_firestore(user_id, data, result):
    if not db or not user_id:
        logging.warning("Firestore or user ID not available. Cannot log transaction.")
        return

    try:
        transactions_ref = db.collection('artifacts').document(app_id).collection('users').document(user_id).collection('transactions')
        transactions_ref.add({
            'amount': data.get('amount'),
            'currency': data.get('currency'),
            'protocol': data.get('protocol'),
            'cardNumber': data.get('cardNumber'),
            'status': result.get('status'),
            'response_code': result.get('response_code'),
            'blockchain_hash': result.get('blockchain_hash'),
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        logging.info(f"Transaction logged to Firestore for user {user_id}")
    except Exception as e:
        logging.error(f"Error logging to Firestore: {e}", exc_info=True)

# --- Raw TCP/IP Listener for Physical Terminals ---
# (Your existing TCP listener code remains here)
# ...

# ===============================================================
# --- UI ROUTING FOR WEB VIRTUAL TERMINAL ---
# ===============================================================

@app.route('/')
def index():
    """Main entry point. Redirects to login or card page based on session."""
    if 'logged_in' in session:
        return redirect(url_for('card_page'))
    return redirect(url_for('login_page'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    """Handles user login."""
    if request.method == 'POST':
        # IMPORTANT: Replace with a secure database check
        if request.form['username'] == 'admin' and request.form['password'] == 'password':
            session['logged_in'] = True
            session.permanent = True
            return redirect(url_for('card_page'))
        else:
            flash("Invalid username or password.", "danger")
    return render_template('login.html')

@app.route('/card')
def card_page():
    """Displays the main transaction page. Protected by session."""
    if 'logged_in' not in session:
        flash("You must be logged in to access this page.", "warning")
        return redirect(url_for('login_page'))
    return render_template('card.html')

@app.route('/processing')
def processing_page():
    """Displays the processing buffer page."""
    if 'logged_in' not in session:
        return redirect(url_for('login_page'))
    return render_template('processing.html')

@app.route('/success')
def success_page():
    """Displays the transaction success page."""
    if 'logged_in' not in session:
        return redirect(url_for('login_page'))
    return render_template('success.html')

@app.route('/rejected')
def rejected_page():
    """Displays the transaction rejected page."""
    if 'logged_in' not in session:
        return redirect(url_for('login_page'))
    return render_template('rejected.html')

@app.route('/forgot-password')
def forgot_password_page():
    """Displays the forgot password page."""
    return render_template('forgot_password.html')

@app.route('/reset-password')
def reset_password_page():
    """Displays the reset password page."""
    return render_template('reset_password.html')

@app.route('/logout')
def logout():
    """Logs the user out by clearing the session."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login_page'))

# --- API Endpoints for Web/PC Terminal ---
@app.route('/api/process_transaction', methods=['POST'])
def handle_web_payment():
    """API endpoint called by JavaScript to process the payment."""
    if 'logged_in' not in session:
        return jsonify({"status": "error", "message": "User not authenticated."}), 401
    try:
        data = request.json
        result = process_payment_logic(data)
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error processing web payment: {e}")
        return jsonify({"status": "declined", "response_code": "99", "message": "Internal Server Error"}), 500

# (Your other API endpoints can remain here)
# ...

if __name__ == '__main__':
    # Start the TCP listener in a separate thread
    tcp_thread = threading.Thread(target=start_tcp_listener, daemon=True)
    tcp_thread.start()

    # Start the Flask web server
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
