import os
import time
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Load environment variables (only needed when running locally)
load_dotenv()

# --- Config ---
PRODUCT_URL = "https://www.marukyu-koyamaen.co.jp/english/shop/products/1186000cc"  # 🔁 Replace with real product URL
STOCK_SELECTOR = "p.stock.single-stock-status"  # 🔁 Replace with correct CSS selector

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID =  "chat_ids.json"
HEADERS = {"User-Agent": "Mozilla/5.0"}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! You started the bot.")

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.run_polling()

if __name__ == "__main__":
    main()

def load_chat_ids():
    if os.path.exists(TELEGRAM_CHAT_ID):
        with open(TELEGRAM_CHAT_ID, "r") as f:
            return json.load(f)
    return []

def save_chat_ids(chat_ids):
    with open(TELEGRAM_CHAT_ID, "w") as f:
        json.dump(chat_ids, f)

# --- Send alert to Telegram ---
def send_telegram_alert(message):
    chat_ids = load_chat_ids()
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    for chat_id in chat_ids:
        payload = {
            "chat_id": chat_id,
            "text": message
        }
        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()
            print(f"✅ Telegram alert sent to {chat_id}.")
        except Exception as e:
            print(f"❌ Failed to send Telegram alert to {chat_id}: {e}")

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
            send_telegram_alert(f"your backside is smelly")
            print("Cooldown for 1 hour...")
            time.sleep(3600)

    except Exception as e:
        print(f"❌ Error checking stock: {e}")

# --- Main loop ---
if __name__ == "__main__":
    print("🛒 Restock bot started.")
    while True:
        check_stock()
        time.sleep(60)  # Check every 10 minutes (600 seconds)