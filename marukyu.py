import os
import json
import time
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

# --- Config ---
PRODUCT_URL = "https://www.marukyu-koyamaen.co.jp/english/shop/products/1186000cc"
STOCK_SELECTOR = "p.stock.single-stock-status"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_IDS_FILE = "chat_ids.json"
HEADERS = {"User-Agent": "Mozilla/5.0"}



# --- Chat ID management ---
def load_chat_ids():
    if os.path.exists(CHAT_IDS_FILE):
        with open(CHAT_IDS_FILE, "r") as f:
            return json.load(f)
    return []

def save_chat_ids(chat_ids):
    with open(CHAT_IDS_FILE, "w") as f:
        json.dump(chat_ids, f)

# --- Telegram /start handler ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Start command received")
    chat_id = str(update.effective_chat.id)
    chat_ids = load_chat_ids()
    if chat_id not in chat_ids:
        chat_ids.append(chat_id)
        save_chat_ids(chat_ids)
        await update.message.reply_text("✅ You are now subscribed to restock alerts!")
    else:
        await update.message.reply_text("You're already subscribed.")

    stock_monitor()

# --- Send alert to all users ---
def send_telegram_alert(message):
    chat_ids = load_chat_ids()
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    for chat_id in chat_ids:
        payload = {"chat_id": chat_id, "text": message}
        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()
            print(f"✅ Alert sent to {chat_id}")
        except Exception as e:
            print(f"❌ Failed to send alert to {chat_id}: {e}")

# --- Stock checker loop ---
async def stock_monitor():
    print("🛒 Restock bot started.")
    while True:
        try:
            response = requests.get(PRODUCT_URL, headers=HEADERS)
            soup = BeautifulSoup(response.text, 'html.parser')
            stock_element = soup.select_one(STOCK_SELECTOR)

            if stock_element:
                status = stock_element.text.strip().lower()
                print(f"[INFO] Current stock status: {status}")

            else:
                # If no stock status found, assume back in stock
                send_telegram_alert(f"🚨 Product is BACK IN STOCK!\n{PRODUCT_URL}")
                await asyncio.sleep(3600)

        except Exception as e:
            print(f"❌ Error checking stock: {e}")

        await asyncio.sleep(60)  # Check every minute

# --- Main app ---
import asyncio

async def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    await (
    stock_monitor(),
    app.run_polling()
    )

    
# Main entry point
if __name__ == "__main__":
    asyncio.run(main())  # Or await main() if you're in a running event loop