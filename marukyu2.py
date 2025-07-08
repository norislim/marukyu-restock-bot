import os, asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Start command received")
    await update.message.reply_text("✅ Bot is working!")

async def main():
    app = ApplicationBuilder().token("7667049151:AAFCFEeY9FmjDjOlREWLs_ta-Fg5V2TTUJk").build()
    app.add_handler(CommandHandler("start", start))
    await app.run_polling()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()