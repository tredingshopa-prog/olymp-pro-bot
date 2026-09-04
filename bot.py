8659134145:AAHt6tQsKwJOP3bxeU8MhUiXQ6GP2t4T4HI
import os
import random
from flask import Flask, request
import telebot
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

bot = telebot.TeleBot(TOKEN)
app = Flask(name)

PAIRS = [
    "AUD/USD", "EUR/AUD", "EUR/CAD", "EUR/CHF",
    "EUR/GBP", "EUR/JPY", "EUR/USD", "GBP/USD",
    "NZD/USD", "USD/CAD", "USD/CHF", "USD/JPY"
]

TIMEFRAMES = ["M1", "M2", "M5", "M10", "M30", "H1"]

user_pair = {}
user_timeframe = {}
last_signal = {}


def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📊 Available Pairs", callback_data="pairs"),
        types.InlineKeyboardButton("📈 Last Signal", callback_data="last"),
        types.InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
        types.InlineKeyboardButton("ℹ️ About", callback_data="about")
    )
    return markup


def pair_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []

    for pair in PAIRS:
        buttons.append(
            types.InlineKeyboardButton(
                pair,
                callback_data="pair_" + pair.replace("/", "_")
            )
        )

    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("🏠 Main Menu", callback_data="menu"))
    return markup


def timeframe_menu():
    markup = types.InlineKeyboardMarkup(row_width=3)

    for tf in TIMEFRAMES:
        markup.add(
            types.InlineKeyboardButton(
                tf,
                callback_data="tf_" + tf
            )
        )

    markup.add(types.InlineKeyboardButton("💱 Change Pair", callback_data="pairs"))
    return markup


def signal_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🔄 New Analysis", callback_data="new"),
        types.InlineKeyboardButton("💱 Change Pair", callback_data="pairs"),
        types.InlineKeyboardButton("⏱ Change Timeframe", callback_data="timeframes"),
        types.InlineKeyboardButton("🏠 Main Menu", callback_data="menu")
    )
    return markup


def make_signal(pair, timeframe):
    signal = random.choice(["BUY", "SELL", "WAIT"])
    confidence = random.randint(65, 88)

    price = round(random.uniform(1.05000, 1.20000), 5)

    if signal == "BUY":
        target = round(price + 0.00080, 5)
        stop = round(price - 0.00050, 5)

        text = f"""
━━━━━━━━━━━━━━━━━━
📊 OLYMP TRADE SIGNAL
━━━━━━━━━━━━━━━━━━

💱 Pair: {pair}
⏱ Timeframe: {timeframe}

🟢 SIGNAL: BUY

📍 Entry: {price}
🎯 Target: {target}
🛑 Stop: {stop}

📈 Confidence: {confidence}%

━━━━━━━━━━━━━━━━━━
⚠️ Demo analysis — not financial advice.
━━━━━━━━━━━━━━━━━━
"""

    elif signal == "SELL":
        target = round(price - 0.00080, 5)
        stop = round(price + 0.00050, 5)

        text = f"""
━━━━━━━━━━━━━━━━━━
📊 OLYMP TRADE SIGNAL
━━━━━━━━━━━━━━━━━━

💱 Pair: {pair}
⏱ Timeframe: {timeframe}

🔴 SIGNAL: SELL

📍 Entry: {price}
🎯 Target: {target}
🛑 Stop: {stop}

📈 Confidence: {confidence}%

━━━━━━━━━━━━━━━━━━
⚠️ Demo analysis — not financial advice.
━━━━━━━━━━━━━━━━━━
"""

    else:
        text = f"""
━━━━━━━━━━━━━━━━━━
📊 OLYMP TRADE SIGNAL
━━━━━━━━━━━━━━━━━━

💱 Pair: {pair}
⏱ Timeframe: {timeframe}

🟡 SIGNAL: WAIT

Market conditions are unclear.

⏳ Recommendation:
Wait for stronger confirmation.

━━━━━━━━━━━━━━━━━━
⚠️ Demo analysis — not financial advice.
━━━━━━━━━━━━━━━━━━
"""

    return signal, text


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Welcome to Olymp Pro BOT!\n\n"
        "Choose an option:",
        reply_markup=main_menu()
    )


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    data = call.data

    if data == "menu":
        bot.edit_message_text(
            "🏠 Main Menu\n\nChoose an option:",
            chat_id,
            call.message.message_id,
            reply_markup=main_menu()
        )

elif data == "pairs":
        bot.edit_message_text(
            "💱 Select currency pair:",
            chat_id,
            call.message.message_id,
            reply_markup=pair_menu()
        )

    elif data.startswith("pair_"):
        pair = data.replace("pair_", "").replace("_", "/")
        user_pair[chat_id] = pair

        bot.edit_message_text(
            f"💱 Pair selected: {pair}\n\n"
            "⏱ Select timeframe:",
            chat_id,
            call.message.message_id,
            reply_markup=timeframe_menu()
        )

    elif data == "timeframes":
        bot.edit_message_text(
            "⏱ Select timeframe:",
            chat_id,
            call.message.message_id,
            reply_markup=timeframe_menu()
        )

    elif data.startswith("tf_"):
        timeframe = data.replace("tf_", "")
        user_timeframe[chat_id] = timeframe

        pair = user_pair.get(chat_id, "EUR/USD")

        signal, text = make_signal(pair, timeframe)
        last_signal[chat_id] = text

        bot.edit_message_text(
            text,
            chat_id,
            call.message.message_id,
            reply_markup=signal_menu()
        )

    elif data == "new":
        pair = user_pair.get(chat_id, "EUR/USD")
        timeframe = user_timeframe.get(chat_id, "M5")

        signal, text = make_signal(pair, timeframe)
        last_signal[chat_id] = text

        bot.edit_message_text(
            text,
            chat_id,
            call.message.message_id,
            reply_markup=signal_menu()
        )

    elif data == "last":
        text = last_signal.get(
            chat_id,
            "📭 No signal yet.\n\nFirst choose a pair and timeframe."
        )

        bot.edit_message_text(
            text,
            chat_id,
            call.message.message_id,
            reply_markup=signal_menu()
        )

    elif data == "settings":
        bot.edit_message_text(
            "⚙️ Settings\n\n"
            "Signal mode: Demo\n"
            "Risk management: Enabled\n\n"
            "Real market-data analysis will be added later.",
            chat_id,
            call.message.message_id,
            reply_markup=main_menu()
        )

    elif data == "about":
        bot.edit_message_text(
            "ℹ️ About Olymp Pro BOT\n\n"
            "This bot is designed to provide market-analysis signals.\n\n"
            "It does not connect to or trade your Olymp Trade account "
            "and does not guarantee profitable trades.",
            chat_id,
            call.message.message_id,
            reply_markup=main_menu()
        )

    bot.answer_callback_query(call.id)


@app.route("/")
def home():
    return "Olymp Pro BOT is running!"


@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    update = types.Update.de_json(request.data.decode("utf-8"))
    bot.process_new_updates([update])
    return "OK"


if name == "main":
    port = int(os.environ.get("PORT", 10000))
    render_url = os.environ.get("RENDER_EXTERNAL_URL")

    if render_url:
        bot.remove_webhook()
        bot.set_webhook(url=render_url + "/telegram")

    app.run(
        host="0.0.0.0",
        port=port
)
