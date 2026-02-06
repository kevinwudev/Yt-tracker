import asyncio
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import os
import logging
from dotenv import load_dotenv
from datetime import date, timedelta


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def send_msg(text_msg):

        yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

        if text_msg == "": text_msg = f"There is no published videos in {yesterday}!  (UTC+0)"

        bot = Bot(token=BOT_TOKEN)

        await bot.send_message(
             chat_id=CHAT_ID,
             text=f"{text_msg}"
             )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

def call_start():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    application.run_polling()

if __name__ == "__main__":

    text_msg = f"""TG Test"""
    print(BOT_TOKEN, "\n", CHAT_ID)
    asyncio.run(send_msg(text_msg))
