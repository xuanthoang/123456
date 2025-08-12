import os
import json
from flask import Flask, request, render_template
from binance.client import Client
from binance.enums import *
from dotenv import load_dotenv

# Load biến môi trường từ file .env nếu tồn tại (local)
if os.path.exists(".env"):
    load_dotenv()

app = Flask(__name__)

# Lấy API key và secret từ biến môi trường
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
WEBHOOK_PASSPHRASE = os.getenv("WEBHOOK_PASSPHRASE")

# Kiểm tra API key khi khởi động
if not API_KEY or not API_SECRET or not WEBHOOK_PASSPHRASE:
    raise ValueError("❌ Missing API_KEY, API_SECRET, or WEBHOOK_PASSPHRASE in environment variables.")

client = Client(API_KEY, API_SECRET, tld='us')

def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        print(f"[ORDER] {order_type} - {side} {quantity} {symbol}")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        return order
    except Exception as e:
        print(f"❌ Exception occurred - {e}")
        return False

@app.route('/')
def welcome():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    data = json.loads(request.data)
    
    # Bảo mật bằng passphrase
    if data.get('passphrase') != WEBHOOK_PASSPHRASE:
        return {"code": "error", "message": "Nice try, invalid passphrase"}

    side = data['strategy']['order_action'].upper()
    quantity = data['strategy']['order_contracts']
    order_response = order(side, quantity, "DOGEUSD")

    if order_response:
        return {"code": "success", "message": "order executed"}
    else:
        return {"code": "error", "message": "order failed"}

if __name__ == '__main__':
    app.run(debug=True)
