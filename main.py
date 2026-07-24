import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# ضع توكن البوت والـ ID الخاص بك كأدمن
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
ADMIN_ID = 123456789  # استبدله بـ ID تيليجرام الخاص بك

bot = telebot.TeleBot(BOT_TOKEN)

# قائمة المشتركين (تخزين مؤقت في الذاكرة)
paid_users = {ADMIN_ID}

# ================= 1. أمر البداية للمشتركين =================
@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    if user_id in paid_users:
        markup = InlineKeyboardMarkup()
        # ضع رابط الموقع المنشور (GitHub Pages أو Vercel)
        web_app = WebAppInfo(url="https://YOUR_WEB_APP_URL_HERE")
        markup.add(InlineKeyboardButton("💻 فتح المنصة التعليمية", web_app=web_app))
        
        bot.reply_to(message, f"مرحباً بك {message.from_user.first_name} في المنصة!", reply_markup=markup)
    else:
        bot.reply_to(message, "⚠️ هذه المنصة خاصة للمشتركين فقط. يرجى التواصل مع الإدارة للاشتراك.")

# ================= 2. أوامر الأدمن (Admin Commands) =================
@bot.message_handler(commands=['admin'])
def admin_cmd(message):
    if message.from_user.id != ADMIN_ID:
        return
    text = (
        "🛠️ **لوحة تحكم الأدمن**\n\n"
        "• `/adduser [ID]` - تفعيل اشتراك مستخدم\n"
        "• `/deluser [ID]` - إلغاء اشتراك مستخدم\n"
        "• `/users` - عرض عدد المشتركين\n"
        "• `/broadcast [الرسالة]` - إرسال إذاعة لجميع المشتركين"
    )
    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['adduser'])
def add_user_cmd(message):
    if message.from_user.id == ADMIN_ID:
        try:
            uid = int(message.text.split()[1])
            paid_users.add(uid)
            bot.reply_to(message, f"✅ تم تفعيل الاشتراك للمستخدم: `{uid}`", parse_mode="Markdown")
        except:
            bot.reply_to(message, "❌ الاستخدام الصحيح: `/adduser 123456789`", parse_mode="Markdown")

@bot.message_handler(commands=['deluser'])
def del_user_cmd(message):
    if message.from_user.id == ADMIN_ID:
        try:
            uid = int(message.text.split()[1])
            paid_users.discard(uid)
            bot.reply_to(message, f"❌ تم إلغاء اشتراك المستخدم: `{uid}`", parse_mode="Markdown")
        except:
            bot.reply_to(message, "❌ الاستخدام الصحيح: `/deluser 123456789`", parse_mode="Markdown")

@bot.message_handler(commands=['users'])
def list_users_cmd(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, f"📊 عدد المشتركين الحاليين: **{len(paid_users)}**", parse_mode="Markdown")

bot.polling(none_stop=True)
