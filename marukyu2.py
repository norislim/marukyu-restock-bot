from dotenv import load_dotenv
import os

load_dotenv()
print("DEBUG BOT TOKEN:", os.getenv("TELEGRAM_BOT_TOKEN"))