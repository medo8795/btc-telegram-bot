import telebot
from telebot import types
from flask import Flask, request
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
import os
import arabic_reshaper
from bidi.algorithm import get_display

# ============================================================
#                      إعدادات البوتين
# ============================================================

TOKEN_1 = os.environ.get('TOKEN_1') or "8380502228:AAFQ0M1fcpPll9xCD2h9_Ce1KeCVAAjAnio"
bot1 = telebot.TeleBot(TOKEN_1, threaded=False)

TOKEN_2 = os.environ.get('TOKEN_2') or "8742379864:AAFj8c0SgFItHbZXC_cv6SVBNvKMXHETmlo"
bot2 = telebot.TeleBot(TOKEN_2, threaded=False)

app = Flask(__name__)

BASE_URL = os.environ.get('BASE_URL') or "https://btc-telegram-bot-vnz4.onrender.com"

# ============================================================
#               Webhook Routes للبوتين
# ============================================================

@app.route('/webhook1', methods=['POST'])
def webhook_bot1():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = types.Update.de_json(json_string)
        bot1.process_new_updates([update])
        return "!", 200
    return "Error", 403

@app.route('/webhook2', methods=['POST'])
def webhook_bot2():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = types.Update.de_json(json_string)
        bot2.process_new_updates([update])
        return "!", 200
    return "Error", 403

@app.route('/')
def home():
    bot1.remove_webhook()
    bot1.set_webhook(url=BASE_URL + '/webhook1')
    bot2.remove_webhook()
    bot2.set_webhook(url=BASE_URL + '/webhook2')
    return "✅ كلا البوتين يعملان بنجاح!", 200

# ============================================================
#               منطق البوت الأول - حاسبة BTC
# ============================================================

@bot1.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "✨ **مرحباً بك في حاسبة BTC الاحترافية** ✨\n\n"
        "يرجى إرسال سعر جرام **عيار 21** الآن\n"
        "وسأقوم بحساب كافة السبائك والعملات شاملة المصنعية."
    )
    bot1.reply_to(message, welcome_text, parse_mode='Markdown')

@bot1.message_handler(func=lambda message: True)
def calculate_prices(message):
    try:
        input_text = message.text.replace(',', '')
        p21 = float(input_text)
        p24 = p21 * 24 / 21

        response = f"📊 **تقرير أسعار الذهب شامل المصنعية**\n"
        response += f"─── عيار 21: `{p21:,.0f}` | عيار 24: `{p24:,.0f}` ───\n\n"

        response += "📀 **سبائك BTC (عيار 24)**\n"
        response += "━━━━━━━━━━━━━━\n"

        bullions = [
            ("سبيكة 1 جرام", 1, 185), ("سبيكة 2.5 جرام", 2.5, 110),
            ("سبيكة 5 جرام", 5, 85), ("سبيكة 10 جرام", 10, 82),
            ("سبيكة 20 جرام", 20, 80), ("أونصة 31.1 جرام", 31.1, 79),
            ("سبيكة 50 جرام", 50, 77), ("سبيكة 100 جرام", 100, 75)
        ]

        for name, w, fee in bullions:
            total = w * (p24 + fee)
            response += f"📍 *{name}*\n"
            response += f"└ المصنعية: `{fee}` ج/جرام\n"
            response += f"└ **السعر النهائي: `{total:,.0f}` ج.م**\n"
            response += "────────────────\n"

        response += "\n🪙 **عملات BTC (عيار 21)**\n"
        response += "━━━━━━━━━━━━━━\n"

        coins = [
            ("جنيه ذهب (8 جرام)", 8, 75),
            ("نصف جنيه (4 جرام)", 4, 80),
            ("ربع جنيه (2 جرام)", 2, 85)
        ]

        for name, w, fee in coins:
            total = w * (p21 + fee)
            response += f"📍 *{name}*\n"
            response += f"└ المصنعية: `{fee}` ج/جرام\n"
            response += f"└ **السعر النهائي: `{total:,.0f}` ج.م**\n"
            response += "────────────────\n"

        response += "\n⚠️ *ملاحظة: الأسعار شاملة المصنعية والدمغة وفقاً لآخر تحديث لشركة BTC.*"
        bot1.reply_to(message, response, parse_mode='Markdown')

    except ValueError:
        bot1.reply_to(message, "⚠️ يرجى إرسال السعر بالأرقام فقط (مثلاً: 3550)")
    except Exception as e:
        print(f"Bot1 Error: {e}")
        bot1.reply_to(message, "❌ حدث خطأ أثناء معالجة البيانات، يرجى المحاولة لاحقاً.")

# ============================================================
#               منطق البوت الثاني - صورة الذهب
# ============================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

days_ar = {
    "Monday": "الإثنين", "Tuesday": "الثلاثاء", "Wednesday": "الأربعاء",
    "Thursday": "الخميس", "Friday": "الجمعة", "Saturday": "السبت", "Sunday": "الأحد"
}

months_ar = {
    "January": "يناير", "February": "فبراير", "March": "مارس", "April": "أبريل",
    "May": "مايو", "June": "يونيو", "July": "يوليو", "August": "أغسطس",
    "September": "سبتمبر", "October": "أكتوبر", "November": "نوفمبر", "December": "ديسمبر"
}

def reshape_arabic(text):
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

def format_price(value):
    int_val = int(value)
    if value == int_val:
        return f"{int_val:,}"
    return f"{value:,}"

def create_gold_image(price_21):
    price_24 = round(price_21 * 24 / 21)
    price_18 = round(price_21 * 18 / 21)
    price_coin = round(price_21 * 8)
    price_ounce = round(price_21 * 24 / 21 * 31.1)

    now = datetime.now() + timedelta(hours=2)
    day_name = days_ar.get(now.strftime('%A'), '')
    month_name = months_ar.get(now.strftime('%B'), '')
    date_text = reshape_arabic(f"{day_name}، {now.strftime('%d')} {month_name}")
    time_text = f"{'ص' if now.strftime('%p') == 'AM' else 'م'} {now.strftime('%I:%M')}"

    design_path = os.path.join(SCRIPT_DIR, "design.jpg")
    font_path = os.path.join(SCRIPT_DIR, "font.ttf")
    amiri_path = os.path.join(SCRIPT_DIR, "amiri.ttf")

    try:
        if not os.path.exists(design_path) or not os.path.exists(font_path):
            return "missing_files"

        img = Image.open(design_path).convert("RGB")
        draw = ImageDraw.Draw(img)

        font_prices = ImageFont.truetype(font_path, 42)
        font_date = ImageFont.truetype(amiri_path, 25)
        text_color = "#232528"

        draw.text((579, 368), date_text, fill=text_color, font=font_date, anchor="mm")
        draw.text((288, 368), time_text, fill=text_color, font=font_date, anchor="mm")
        draw.text((370, 468), format_price(price_18), fill=text_color, font=font_prices, anchor="mm")
        draw.text((370, 543), format_price(price_21), fill=text_color, font=font_prices, anchor="mm")
        draw.text((370, 623), format_price(price_24), fill=text_color, font=font_prices, anchor="mm")
        draw.text((370, 704), format_price(price_coin), fill=text_color, font=font_prices, anchor="mm")
        draw.text((370, 791), format_price(price_ounce), fill=text_color, font=font_prices, anchor="mm")

        output_path = os.path.join(SCRIPT_DIR, "output_result.jpg")
        img.save(output_path, "JPEG", quality=100, optimize=True)
        return output_path

    except Exception as e:
        print(f"Bot2 Image Error: {e}")
        return None

@bot2.message_handler(func=lambda message: True)
def handle_price(message):
    user_input = message.text.strip()

    if user_input.replace('.', '', 1).isdigit():
        price_21 = float(user_input)
        bot2.send_chat_action(message.chat.id, 'upload_photo')
        result = create_gold_image(price_21)

        if result == "missing_files":
            bot2.reply_to(message, "❌ خطأ: ملفات design.jpg أو font.ttf غير موجودة في السيرفر.")
        elif result:
            with open(result, 'rb') as photo:
                caption_msg = (
                    f"✅ تم تحديث الأسعار بنجاح:\n"
                    f"🔸 عيار 21: {format_price(price_21)}\n"
                    f"🔸 الجنيه الذهب: {round(price_21 * 8):,}\n"
                    f"🔸 الأوقية: {round(price_21 * 24 / 21 * 31.1):,}"
                )
                bot2.send_photo(message.chat.id, photo, caption=caption_msg)
        else:
            bot2.reply_to(message, "❌ حدث خطأ فني أثناء تصميم الصورة.")
    else:
        bot2.reply_to(message, "⚠️ أرسل سعر الذهب (أرقام فقط) لعيار 21.")

# ============================================================
#                        تشغيل التطبيق
# ============================================================

if __name__ == "__main__":
    bot1.remove_webhook()
    bot1.set_webhook(url=BASE_URL + '/webhook1')
    bot2.remove_webhook()
    bot2.set_webhook(url=BASE_URL + '/webhook2')
    print("✅ Webhooks registered!")
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8080)))
