import telebot
from flask import Flask, request
import os

# --- إعدادات البوت ---
TOKEN = "8380502228:AAFQ0M1fcpPll9xCD2h9_Ce1KeCVAAjAnio"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# تصحيح الرابط بإضافة / قبل التوكن
WEBHOOK_URL = "https://btc-telegram-bot-vnz4.onrender.com/" + TOKEN 

@app.route('/' + TOKEN, methods=['POST'])
def get_message():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "!", 200
    else:
        return "Error", 403

@app.route('/')
def home():
    # تفعيل الـ Webhook تلقائياً عند زيارة الرابط الأساسي أو تشغيل السيرفر
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    return "Bot is Alive and Webhook is Set!", 200

# --- منطق البوت ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "✨ **مرحباً بك في حاسبة BTC الاحترافية** ✨\n\n"
        "يرجى إرسال سعر جرام **عيار 21** الآن\n"
        "وسأقوم بحساب كافة السبائك والعملات شاملة المصنعية."
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def calculate_prices(message):
    try:
        # التأكد من تحويل النص إلى رقم واستبدال الفاصلة لو وجدت
        price_text = message.text.replace(',', '')
        p21 = float(price_text)
        p24 = p21 * 24 / 21
        
        response = "📊 **تقرير أسعار الذهب شامل المصنعية**\n"
        response += f"─── عيار 21: `{p21:,.0f}` | عيار 24: `{p24:,.0f}` ───\n\n"
        
        response += "📀 **سبائك BTC (عيار 24)**\n━━━━━━━━━━━━━━\n"
        bullions = [
            ("سبيكة 1 جرام", 1, 185), ("سبيكة 2.5 جرام", 2.5, 110), 
            ("سبيكة 5 جرام", 5, 85), ("سبيكة 10 جرام", 10, 82), 
            ("سبيكة 20 جرام", 20, 80), ("أونصة 31.1 جرام", 31.1, 79), 
            ("سبيكة 50 جرام", 50, 77), ("سبيكة 100 جرام", 100, 75)
        ]
        for name, w, fee in bullions:
            total = w * (p24 + fee)
            response += f"📍 *{name}*\n└ المصنعية: `{fee}` ج/جرام\n└ **السعر النهائي: `{total:,.0f}` ج.م**\n────────────────\n"

        response += "\n🪙 **عملات BTC (عيار 21)**\n━━━━━━━━━━━━━━\n"
        coins = [
            ("جنيه ذهب (8 جرام)", 8, 75), 
            ("نصف جنيه (4 جرام)", 4, 80), 
            ("ربع جنيه (2 جرام)", 2, 85)
        ]
        for name, w, fee in coins:
            total = w * (p21 + fee)
            response += f"📍 *{name}*\n└ المصنعية: `{fee}` ج/جرام\n└ **السعر النهائي: `{total:,.0f}` ج.م**\n────────────────\n"

        response += "\n⚠️ *ملاحظة: الأسعار تقريبية وشاملة المصنعية والدمغة.*"
        bot.reply_to(message, response, parse_mode="Markdown")
    except ValueError:
        bot.reply_to(message, "⚠️ من فضلك ابعت السعر أرقام بس (مثال: 3550)")

if __name__ == "__main__":
    # تشغيل السيرفر محلياً للتجربة
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8080)))
