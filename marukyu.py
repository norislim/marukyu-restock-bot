import os
import time
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables (only needed when running locally)
load_dotenv()

# --- Config ---
PRODUCT_URL = "https://www.marukyu-koyamaen.co.jp/english/shop/products/1186000cc"  # 🔁 Replace with real product URL
STOCK_SELECTOR = "p.stock.single-stock-status"  # 🔁 Replace with correct CSS selector

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
HEADERS = {"User-Agent": "Mozilla/5.0"}

# --- Send alert to Telegram ---
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print("✅ Telegram alert sent.")
    except Exception as e:
        print(f"❌ Failed to send Telegram alert: {e}")

# --- Check the stock status ---
def check_stock():
    try:
        response = requests.get(PRODUCT_URL, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')

        stock_element = soup.select_one(STOCK_SELECTOR)
        if stock_element:
            status = stock_element.text.strip().lower()
            print(f"[INFO] Current stock status: {status}")

        else:
            send_telegram_alert(f"🚨 Product is BACK IN STOCK!\n{PRODUCT_URL}")

    except Exception as e:
        print(f"❌ Error checking stock: {e}")

# --- Main loop ---
if __name__ == "__main__":
    print("🛒 Restock bot started.")
    while True:
        check_stock()
        time.sleep(60)  # Check every 10 minutes (600 seconds)