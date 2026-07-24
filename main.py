import threading
import time
from flask import Flask
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
ADMIN_ID = 5907227359

bot = telebot.TeleBot(BOT_TOKEN)
all_users = set()

app = Flask(__name__)

@app.route('/')
def home():
    return "Server is active"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive_ping():
    while True:
        time.sleep(600)

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    all_users.add(user_id)
    
    markup = InlineKeyboardMarkup()
    web_app = WebAppInfo(url="https://YOUR_WEB_APP_URL_HERE")
    markup.add(InlineKeyboardButton("💻 فتح منصة ناصر التعليمية", web_app=web_app))
    
    welcome_text = f"مرحباً بك يا {message.from_user.first_name} في المنصة التعليمية! 🎓\n\nاضغط على الزر أدناه لفتح التطبيق مباشرة:"
    bot.reply_to(message, welcome_text, reply_markup=markup)

@bot.message_handler(commands=['admin'])
def admin_cmd(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    text = "🛠️ **لوحة تحكم الأدمن**\n\n• `/stats` - عرض عدد المستخدمين والزوار\n• `/bc [الرسالة]` - إرسال إشعار/إذاعة لجميع مستخدمي البوت"
    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['stats'])
def stats_cmd(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, f"📊 إجمالي عدد مستخدمي البوت: **{len(all_users)}**", parse_mode="Markdown")

@bot.message_handler(commands=['bc'])
def broadcast_cmd(message):
    if message.from_user.id == ADMIN_ID:
        msg_text = message.text.replace('/bc ', '').strip()
        if not msg_text or msg_text == '/bc':
            bot.reply_to(message, "⚠️ يرجى كتابة الرسالة بعد الأمر، مثال:\n`/bc أهلاً بكم، تم تحديث المواد`", parse_mode="Markdown")
            return
        
        count = 0
        for uid in all_users:
            try:
                bot.send_message(uid, f"📢 **إشعار من الإدارة:**\n\n{msg_text}", parse_mode="Markdown")
                count += 1
            except:
                pass
        bot.reply_to(message, f"✅ تم إرسال الإشعار بنجاح إلى {count} مستخدم.")

if __name__ == "__main__":
    t_flask = threading.Thread(target=run_flask)
    t_flask.daemon = True
    t_flask.start()

    t_ping = threading.Thread(target=keep_alive_ping)
    t_ping.daemon = True
    t_ping.start()

    bot.polling(none_stop=True)
