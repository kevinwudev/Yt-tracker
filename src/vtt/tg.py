import asyncio
from httpx import Client
from pydantic_core.core_schema import frozenset_schema
from telegram import (
    Bot,
    InlineKeyboardButton,
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
)
from telegram._utils.defaultvalue import DEFAULT_20
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    filters,
    MessageHandler,
)
import os
import logging
from dotenv import load_dotenv
from datetime import date, timedelta
from vtt.llm import OPENAI_API_KEY, summarize, translate, rewrite
from vtt.google_auth import fetch_calendars, fetch_emails, get_google_service
from openai import OpenAI

load_dotenv()

BTN_SUM = "摘要"
BTN_REWRITE = "改寫"
BTN_TRANS = "翻譯"
BTN_GMAIL = "Gmail"
BTN_CAL = "Calendar"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
client = OpenAI(api_key=OPENAI_API_KEY)


keyboard = ReplyKeyboardMarkup(
    [[BTN_SUM, BTN_REWRITE, BTN_TRANS], [BTN_GMAIL, BTN_CAL]],
    resize_keyboard=True,
)


async def start(update, context):
    context.user_data["waiting_action"] = None
    await update.message.reply_text("選一個功能: ", reply_markup=keyboard)


async def send_msg(text_msg):

    yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

    if text_msg == "":
        text_msg = f"There is no published videos in {yesterday}!  (UTC+0)"

    bot = Bot(token=BOT_TOKEN)

    await bot.send_message(chat_id=CHAT_ID, text=f"{text_msg}")


async def inital_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!"
    )


async def echo(update: Update, context_type: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(update.message.text)


# ===================
# Bot carry
# ====================


async def choose_mode(update, context):
    choice = update.message.text

    if choice == BTN_SUM:
        context.user_data["waiting_action"] = "summarize"
        await update.message.reply_text("請貼上摘要文字: ", reply_markup=keyboard)
        return

    if choice == BTN_REWRITE:
        context.user_data["waiting_action"] = "rewrite"
        await update.message.reply_text("請貼上改寫文字", reply_markup=keyboard)
        return

    if choice == BTN_TRANS:
        context.user_data["waiting_action"] = "translate"
        await update.message.reply_text("請貼上翻譯文字:", reply_markup=keyboard)
        return

    context.user_data["waiting_action"] = None

    if choice == BTN_GMAIL:
        await update.message.reply_text("整理你的gmail")

        gmail = get_google_service("gmail", "v1")
        gmail_info = fetch_emails(gmail, "newer_than:1d", 10)

        await update.message.reply_text(f"回復gmail context \n {gmail_info}")
        return

    if choice == BTN_CAL:
        await update.message.reply_text("整理行事曆...")

        calendar = get_google_service("calendar", "v3")
        calendar_info = fetch_calendars(calendar)

        await update.message.reply_text(f"你的行事曆: \n {calendar_info}")
        return


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    action = context.user_data.get("waiting_action")
    if not action:
        await update.message.reply_text("Please input /summarize, /translate, /rewrite")
        return

    text = update.message.text
    if action == "summarize":
        result = summarize(text)
    elif action == "translate":
        result = translate(text)
    elif action == "rewrite":
        result = rewrite(text)

    await update.message.reply_text(result, reply_markup=keyboard)
    context.user_data["waiting_action"] = None


def call_initial_start():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)
    application.run_polling()


def call_main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(
            filters.Regex(
                f"^({BTN_SUM}|{BTN_CAL}|{BTN_GMAIL}|{BTN_REWRITE}|{BTN_TRANS})$"
            ),
            choose_mode,
        )
    )
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()


if __name__ == "__main__":
    text_msg = f"""TG Test"""
    print(BOT_TOKEN, "\n", CHAT_ID)
    # asyncio.run(send_msg(text_msg))
    gmail = get_google_service("gmail", "v1")
    calendar = get_google_service("calendar", "v3")

    gmail_info = fetch_emails(gmail, "newer_than:1d", 10)
    calendar_info = fetch_calendars(calendar)

    call_main()
