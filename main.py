import telebot
from flask import Flask, request
import os

# --- إعدادات البوت ---
TOKEN = "8380502228:AAFQ0M1fcpPll9xCD2h9_Ce1KeCVAAjAnio"
# إضافة threaded=False لضمان استقرار الرد
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

WEBHOOK_URL = "https://btc-telegram-bot-vnz4.onrender.com/" + TOKEN 

@app.route('/' + TOKEN, methods=['POST'])
def get_message():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "!", 200
    return "Error", 403

@app.route('/')
def home():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    return "Bot is Alive!", 200

# --- منطق البوت ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك! ابعت سعر جرام 21 دلوقتي.")

@bot.message_handler(func=lambda message: True)
def calculate_prices(message):
    try:
        # طباعة للتأكد من وصول الرسالة للدالة
        print(f"Processing price: {message.text}")
        
        p21 = float(message.text.replace(',', ''))
        p24 = p21 * 24 / 21
        
        # رسالة مبسطة جداً للتجربة (بدون مارك داون معقد)
        response = f"تقرير الأسعار:\n"
        response += f"عيار 21: {p21:,.0f}\n"
        response += f"عيار 24: {p24:,.0f}\n"
        response += "------------------\n"
        
        # سبيكة واحدة للتجربة
        total_1g = 1 * (p24 + 185)
        response += f"سبيكة 1 جرام: {total_1g:,.0f} ج.م"

        bot.reply_to(message, response)
        print("Reply sent successfully!")
        
    except Exception as e:
        print(f"Error occurred: {e}")
        bot.reply_to(message, "⚠️ ابعت الرقم صحيح (مثال: 3600)")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8080)))
