
import os
import sys
import json
import random
import secrets
import subprocess
import threading
import time
import flask
import telebot
from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)

import code_runner
from subjects_data import SUBJECTS, get_subject

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
WEB_APP_URL = "https://YOUR_WEB_APP_URL_HERE"
ADMIN_ID = 5907227359

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRACE_WORKER_PATH = os.path.join(BASE_DIR, "trace_worker.py")

bot = telebot.TeleBot(BOT_TOKEN)
all_users = set()

app = flask.Flask(__name__)


@app.route('/')
def home():
    return "Server is active"


def run_flask():
    app.run(host='0.0.0.0', port=8080)


def keep_alive_ping():
    while True:
        time.sleep(600)


# أدوات مساعدة عامة

def edit_or_send(chat_id, message_id, text, markup=None):
    """يحاول تعديل رسالة موجودة، وإن تعذّر يرسل رسالة جديدة."""
    if message_id is not None:
        try:
            bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=markup)
            return
        except Exception:
            pass
    bot.send_message(chat_id, text, reply_markup=markup)


def cancel_markup():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("❌ إلغاء", callback_data="cancel"))
    return kb


def back_button(callback_data, text="🔙 رجوع"):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text, callback_data=callback_data))
    return kb


def main_menu_markup(user_id):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton("💻 فتح المنصة التعليمية", web_app=WebAppInfo(url=WEB_APP_URL)))
    kb.add(
        InlineKeyboardButton("📚 المواد", callback_data="materials"),
        InlineKeyboardButton("🎯 كويز", callback_data="quiz_get"),
    )
    kb.add(
        InlineKeyboardButton("🧪 حل كود", callback_data="solve_menu"),
        InlineKeyboardButton("🔍 تتبع كود", callback_data="trace_start"),
    )
    kb.add(
        InlineKeyboardButton("🏆 لوحة الصدارة", callback_data="leaderboard"),
        InlineKeyboardButton("ℹ️ عن المنصة", callback_data="about"),
    )
    if user_id == ADMIN_ID:
        kb.add(InlineKeyboardButton("👑 لوحة الأدمن", callback_data="admin_menu"))
    return kb


# /start

@bot.message_handler(commands=['start'])
def start_cmd(message):
    all_users.add(message.from_user.id)
    name = message.from_user.first_name or "صديقي"
    text = f"أهلاً {name}! 👋\n\nبوت طلاب تقنية المعلومات 🎓\nاستخدم الأزرار بالأسفل للتنقل بين كل الخدمات:"
    bot.send_message(message.chat.id, text, reply_markup=main_menu_markup(message.from_user.id))


# المواد (Materials)

PAGE_SIZE = 8


def show_materials(chat_id, message_id, page=0, admin_pick_mode=False):
    start = page * PAGE_SIZE
    chunk = SUBJECTS[start:start + PAGE_SIZE]

    kb = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for s in chunk:
        cb = f"admin_addres_subj:{s['id']}" if admin_pick_mode else f"subj:{s['id']}"
        buttons.append(InlineKeyboardButton(s['code'], callback_data=cb))
    kb.add(*buttons)

    page_prefix = "admin_addres_page" if admin_pick_mode else "materials_page"
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("◀️ السابق", callback_data=f"{page_prefix}:{page-1}"))
    if start + PAGE_SIZE < len(SUBJECTS):
        nav_row.append(InlineKeyboardButton("التالي ▶️", callback_data=f"{page_prefix}:{page+1}"))
    if nav_row:
        kb.row(*nav_row)

    kb.add(InlineKeyboardButton("🔙 رجوع", callback_data="admin_menu" if admin_pick_mode else "home"))

    title = "🗂️ اختر المادة لإضافة مرجع لها:" if admin_pick_mode else \
        "📚 اختر مادة لعرض مرجعها، شيتاتها، وأسئلة سنواتها:"
    edit_or_send(chat_id, message_id, title, kb)


def show_subject_detail(chat_id, message_id, subject_id):
    subject = get_subject(subject_id)
    if not subject:
        edit_or_send(chat_id, message_id, "⚠️ المادة غير موجودة.", back_button("materials"))
        return

    resources = data_store.get_resources(subject_id)
    kb = InlineKeyboardMarkup(row_width=1)
    for r in resources:
        kb.add(InlineKeyboardButton(f"📎 {r['title']}", url=r['url']))
    kb.add(InlineKeyboardButton("🔙 رجوع للمواد", callback_data="materials"))

    text = f"📘 {subject['name']} ({subject['code']})\n\n"
    text += "المصادر المتاحة:" if resources else "لا توجد مصادر مضافة لهذه المادة بعد."
    edit_or_send(chat_id, message_id, text, kb)


# حل كود (/solve كأزرار)

def show_solve_menu(chat_id, message_id):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🐍 Python", callback_data="solve_lang:python"),
        InlineKeyboardButton("C", callback_data="solve_lang:c"),
    )
    kb.add(
        InlineKeyboardButton("C++", callback_data="solve_lang:cpp"),
        InlineKeyboardButton("Java", callback_data="solve_lang:java"),
    )
    kb.add(InlineKeyboardButton("JavaScript", callback_data="solve_lang:javascript"))
    kb.add(InlineKeyboardButton("🔙 رجوع", callback_data="home"))
    edit_or_send(chat_id, message_id, "🧪 اختر لغة البرمجة:", kb)


def ask_for_code_to_solve(chat_id, lang):
    sent = bot.send_message(chat_id, f"✍️ أرسل الآن كود {lang} كاملاً في رسالة واحدة:", reply_markup=cancel_markup())
    bot.register_next_step_handler(sent, lambda m: process_solve(m, lang))


def process_solve(message, lang):
    bot.send_chat_action(message.chat.id, "typing")
    result = code_runner.run_code(lang, message.text or "")
    text = result["output"] if result["ok"] else f"❌ خطأ: {result['error']}"
    if len(text) > 3900:
        text = text[:3900] + "\n…(تم اقتصاص الناتج)"
    bot.send_message(message.chat.id, text)
    bot.send_message(message.chat.id, "القائمة الرئيسية 👇", reply_markup=main_menu_markup(message.from_user.id))


# تتبع كود (/trace كأزرار)

def ask_for_code_to_trace(chat_id):
    sent = bot.send_message(
        chat_id,
        "✍️ أرسل كود بايثون بسيط لتتبعه سطراً بسطر (يفضّل كود قصير):",
        reply_markup=cancel_markup(),
    )
    bot.register_next_step_handler(sent, process_trace)


def run_trace(code, timeout=5):
    try:
        proc = subprocess.run(
            [sys.executable, TRACE_WORKER_PATH],
            input=code,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "انتهى الوقت المسموح للتنفيذ (Timeout)"}

    if not proc.stdout:
        return {"ok": False, "error": (proc.stderr or "تعذر تشغيل الكود")[:300]}

    try:
        return json.loads(proc.stdout.strip().splitlines()[-1])
    except Exception:
        return {"ok": False, "error": "تعذر تحليل نتيجة التتبع"}


def process_trace(message):
    bot.send_chat_action(message.chat.id, "typing")
    result = run_trace(message.text or "")

    if not result.get("ok"):
        bot.send_message(message.chat.id, f"❌ {result.get('error', 'حدث خطأ غير متوقع')}")
    else:
        steps = result.get("steps", [])
        if not steps:
            bot.send_message(message.chat.id, "لم يتم تنفيذ أي سطر، تأكد من الكود المُرسل.")
        else:
            lines = ["🔍 نتيجة التتبع:\n"]
            for i, step in enumerate(steps[:40], start=1):
                vars_text = ", ".join(f"{k}={v}" for k, v in step["vars"].items()) or "—"
                lines.append(f"{i}. السطر {step['line']}: {step['code']}\n   المتغيرات: {vars_text}")
            if len(steps) > 40:
                lines.append(f"\n… تم عرض أول 40 خطوة من أصل {len(steps)}")
            if result.get("error"):
                lines.append(f"\n⚠️ توقف التنفيذ بسبب: {result['error']}")
            text = "\n".join(lines)
            if len(text) > 3900:
                text = text[:3900] + "\n…(تم اقتصاص الناتج)"
            bot.send_message(message.chat.id, text)

    bot.send_message(message.chat.id, "القائمة الرئيسية 👇", reply_markup=main_menu_markup(message.from_user.id))


def send_random_quiz(chat_id):
    quizzes = data_store.get_all_quizzes()
    if not quizzes:
        bot.send_message(chat_id, "😅 لا توجد كويزات مضافة حالياً، ترقب إضافتها قريباً!", reply_markup=back_button("home"))
        return
    quiz_id = random.choice(list(quizzes.keys()))
    send_quiz_message(chat_id, quiz_id, quizzes[quiz_id])


def send_quiz_message(chat_id, quiz_id, quiz):
    kb = InlineKeyboardMarkup(row_width=1)
    for i, opt in enumerate(quiz["options"]):
        kb.add(InlineKeyboardButton(f"{chr(65 + i)}. {opt}", callback_data=f"quiz_ans:{quiz_id}:{i}"))
    if quiz.get("hint"):
        kb.add(InlineKeyboardButton("💡 تلميح", callback_data=f"quiz_hint:{quiz_id}"))
    kb.add(InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="home"))
    bot.send_message(chat_id, f"🎯 سؤال:\n\n{quiz['question']}", reply_markup=kb)


def handle_quiz_answer(call, quiz_id, idx):
    quiz = data_store.get_quiz(quiz_id)
    if not quiz:
        bot.answer_callback_query(call.id, "هذا السؤال لم يعد متاحاً", show_alert=True)
        return

    is_correct = idx == quiz["correct"]
    name = call.from_user.first_name or "مستخدم"
    data_store.record_answer(call.from_user.id, name, is_correct)

    if is_correct:
        bot.answer_callback_query(call.id, "✅ إجابة صحيحة!")
    else:
        bot.answer_callback_query(
            call.id,
            f"❌ إجابة خاطئة، الصحيحة: {quiz['options'][quiz['correct']]}",
            show_alert=True,
        )

    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("🎯 سؤال آخر", callback_data="quiz_get"))
    kb.add(InlineKeyboardButton("🏆 لوحة الصدارة", callback_data="leaderboard"))
    kb.add(InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="home"))
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=kb)
    except Exception:
        pass


def handle_quiz_hint(call, quiz_id):
    quiz = data_store.get_quiz(quiz_id)
    hint = quiz.get("hint") if quiz else None
    bot.answer_callback_query(call.id, hint or "لا يوجد تلميح لهذا السؤال", show_alert=True)


def show_leaderboard(chat_id, message_id):
    rows = data_store.get_leaderboard(10)
    if not rows:
        text = "🏆 لوحة الصدارة فارغة حالياً، كن أول من يجاوب على كويز!"
    else:
        medals = ["🥇", "🥈", "🥉"]
        lines = ["🏆 أفضل 10 نتائج:\n"]
        for i, (name, score, correct, total) in enumerate(rows):
            medal = medals[i] if i < 3 else f"{i + 1}."
            lines.append(f"{medal} {name} — {score} نقطة ({correct}/{total})")
        text = "\n".join(lines)
    edit_or_send(chat_id, message_id, text, back_button("home"))


def show_about(chat_id, message_id):
    text = (
        "ℹ️ عن منصة كلية تقنية المعلومات\n\n"
        "💻 فتح المنصة — يفتح تطبيق المواد الكامل\n"
        "📚 المواد — تصفح مرجع، شيتات، وأسئلة سنوات كل مادة\n"
        "🧪 حل كود — نفّذ كود Python / C / C++ / Java / JavaScript واحصل على مخرجاته\n"
        "🔍 تتبع كود — تابع تنفيذ كود بايثون سطراً بسطر مع قيم المتغيرات\n"
        "🎯 كويز — أجب على أسئلة عشوائية واجمع نقاط\n"
        "🏆 لوحة الصدارة — أفضل النتائج بين الطلاب"
    )
    edit_or_send(chat_id, message_id, text, back_button("home"))


# لوحة الأدمن

def show_admin_menu(chat_id, message_id):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("📊 الإحصائيات", callback_data="admin_stats"))
    kb.add(InlineKeyboardButton("📢 إرسال إذاعة", callback_data="admin_broadcast"))
    kb.add(InlineKeyboardButton("➕ كويز جديد", callback_data="admin_newquiz"))
    kb.add(InlineKeyboardButton("➕ إضافة مرجع لمادة", callback_data="admin_addres"))
    kb.add(InlineKeyboardButton("🔙 رجوع", callback_data="home"))
    edit_or_send(chat_id, message_id, "👑 لوحة تحكم الأدمن", kb)


def process_broadcast(message):
    text = (message.text or "").strip()
    if not text:
        bot.send_message(message.chat.id, "لم يتم إرسال أي نص، تم الإلغاء.")
        return
    count = 0
    for uid in all_users:
        try:
            bot.send_message(uid, f"📢 إشعار من الإدارة:\n\n{text}")
            count += 1
        except Exception:
            pass
    bot.send_message(message.chat.id, f"✅ تم إرسال الإذاعة إلى {count} مستخدم.")


def start_newquiz_flow(chat_id):
    msg = bot.send_message(chat_id, "1️⃣ اكتب نص السؤال:", reply_markup=cancel_markup())
    bot.register_next_step_handler(msg, newquiz_step_question)


def newquiz_step_question(message):
    question = (message.text or "").strip()
    if not question:
        bot.send_message(message.chat.id, "⚠️ نص فارغ، حاول من جديد.")
        return
    msg = bot.send_message(
        message.chat.id,
        "2️⃣ اكتب الخيارات مفصولة بعلامة |\nمثال: بايثون|جافا|C++",
        reply_markup=cancel_markup(),
    )
    bot.register_next_step_handler(msg, lambda m: newquiz_step_options(m, question))


def newquiz_step_options(message, question):
    options = [o.strip() for o in (message.text or "").split("|") if o.strip()]
    if len(options) < 2:
        bot.send_message(message.chat.id, "⚠️ يجب إدخال خيارين على الأقل مفصولين بـ |، حاول من جديد.")
        return
    options_list = "\n".join(f"{i + 1}. {o}" for i, o in enumerate(options))
    msg = bot.send_message(
        message.chat.id,
        f"3️⃣ الخيارات:\n{options_list}\n\nاكتب رقم الإجابة الصحيحة:",
        reply_markup=cancel_markup(),
    )
    bot.register_next_step_handler(msg, lambda m: newquiz_step_correct(m, question, options))


def newquiz_step_correct(message, question, options):
    try:
        correct = int((message.text or "").strip()) - 1
        if not (0 <= correct < len(options)):
            raise ValueError
    except ValueError:
        bot.send_message(message.chat.id, "⚠️ رقم غير صحيح، حاول من جديد.")
        return

    msg = bot.send_message(
        message.chat.id,
        "4️⃣ اكتب تلميحاً (اختياري)، أو أرسل - للتخطي:",
        reply_markup=cancel_markup(),
    )
    bot.register_next_step_handler(msg, lambda m: newquiz_step_hint(m, question, options, correct))


def newquiz_step_hint(message, question, options, correct):
    hint = (message.text or "").strip()
    if hint in ("-", ""):
        hint = None
    quiz_id = secrets.token_hex(3)
    data_store.add_quiz(quiz_id, question, options, correct, hint)
    bot.send_message(message.chat.id, "✅ تم إنشاء الكويز بنجاح!")
    bot.send_message(message.chat.id, "القائمة الرئيسية 👇", reply_markup=main_menu_markup(message.from_user.id))

def start_addresource_flow(chat_id, subject_id):
    subject = get_subject(subject_id)
    name = subject["name"] if subject else subject_id
    msg = bot.send_message(chat_id, f"📘 إضافة مرجع لمادة: {name}\n\n1️⃣ اكتب عنوان المرجع:", reply_markup=cancel_markup())
    bot.register_next_step_handler(msg, lambda m: addresource_step_title(m, subject_id))


def addresource_step_title(message, subject_id):
    title = (message.text or "").strip()
    if not title:
        bot.send_message(message.chat.id, "⚠️ العنوان فارغ، حاول من جديد.")
        return
    msg = bot.send_message(message.chat.id, "2️⃣ اكتب رابط المرجع (PDF أو رابط خارجي):", reply_markup=cancel_markup())
    bot.register_next_step_handler(msg, lambda m: addresource_step_url(m, subject_id, title))


def addresource_step_url(message, subject_id, title):
    url = (message.text or "").strip()
    if not url.startswith(("http://", "https://")):
        bot.send_message(message.chat.id, "⚠️ الرابط يجب أن يبدأ بـ http:// أو https://، حاول من جديد.")
        return
    data_store.add_resource(subject_id, title, url)
    bot.send_message(message.chat.id, "✅ تم إضافة المرجع بنجاح!")
    bot.send_message(message.chat.id, "القائمة الرئيسية 👇", reply_markup=main_menu_markup(message.from_user.id))


@bot.message_handler(commands=['admin'])
def admin_cmd(message):
    if message.from_user.id != ADMIN_ID:
        return
    show_admin_menu(message.chat.id, None)


@bot.message_handler(commands=['stats'])
def stats_cmd(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, f"📊 إجمالي عدد مستخدمي البوت: {len(all_users)}")


@bot.message_handler(commands=['bc'])
def broadcast_cmd(message):
    if message.from_user.id != ADMIN_ID:
        return
    msg_text = message.text.replace('/bc ', '').strip()
    if not msg_text or msg_text == '/bc':
        bot.reply_to(message, "⚠️ يرجى كتابة الرسالة بعد الأمر، مثال:\n/bc أهلاً بكم، تم تحديث المواد")
        return
    count = 0
    for uid in all_users:
        try:
            bot.send_message(uid, f"📢 إشعار من الإدارة:\n\n{msg_text}")
            count += 1
        except Exception:
            pass
    bot.reply_to(message, f"✅ تم إرسال الإشعار بنجاح إلى {count} مستخدم.")



@bot.callback_query_handler(func=lambda c: True)
def handle_callbacks(call):
    data = call.data or ""
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    msg_id = call.message.message_id

    try:
        if data == "home":
            bot.answer_callback_query(call.id)
            edit_or_send(chat_id, msg_id, "القائمة الرئيسية 👇", main_menu_markup(user_id))

        elif data == "cancel":
            try:
                bot.clear_step_handler_by_chat_id(chat_id)
            except Exception:
                pass
            bot.answer_callback_query(call.id, "تم الإلغاء")
            edit_or_send(chat_id, msg_id, "تم الإلغاء ✅\n\nالقائمة الرئيسية 👇", main_menu_markup(user_id))

        elif data == "materials" or data.startswith("materials_page:"):
            page = int(data.split(":")[1]) if ":" in data else 0
            bot.answer_callback_query(call.id)
            show_materials(chat_id, msg_id, page)

        elif data.startswith("subj:"):
            bot.answer_callback_query(call.id)
            show_subject_detail(chat_id, msg_id, data.split(":", 1)[1])

        elif data == "solve_menu":
            bot.answer_callback_query(call.id)
            show_solve_menu(chat_id, msg_id)

        elif data.startswith("solve_lang:"):
            bot.answer_callback_query(call.id)
            ask_for_code_to_solve(chat_id, data.split(":", 1)[1])

        elif data == "trace_start":
            bot.answer_callback_query(call.id)
            ask_for_code_to_trace(chat_id)

        elif data == "quiz_get":
            bot.answer_callback_query(call.id)
            send_random_quiz(chat_id)

        elif data.startswith("quiz_ans:"):
            _, quiz_id, idx = data.split(":")
            handle_quiz_answer(call, quiz_id, int(idx))

        elif data.startswith("quiz_hint:"):
            handle_quiz_hint(call, data.split(":", 1)[1])

        elif data == "leaderboard":
            bot.answer_callback_query(call.id)
            show_leaderboard(chat_id, msg_id)

        elif data == "about":
            bot.answer_callback_query(call.id)
            show_about(chat_id, msg_id)

        elif data == "admin_menu":
            if user_id != ADMIN_ID:
                bot.answer_callback_query(call.id, "غير مصرح لك", show_alert=True)
                return
            bot.answer_callback_query(call.id)
            show_admin_menu(chat_id, msg_id)

        elif data == "admin_stats":
            if user_id != ADMIN_ID:
                return
            bot.answer_callback_query(call.id)
            bot.send_message(chat_id, f"📊 إجمالي عدد مستخدمي البوت: {len(all_users)}")

        elif data == "admin_broadcast":
            if user_id != ADMIN_ID:
                return
            bot.answer_callback_query(call.id)
            msg = bot.send_message(chat_id, "✍️ أرسل نص الإذاعة الآن:", reply_markup=cancel_markup())
            bot.register_next_step_handler(msg, process_broadcast)

        elif data == "admin_newquiz":
            if user_id != ADMIN_ID:
                return
            bot.answer_callback_query(call.id)
            start_newquiz_flow(chat_id)

        elif data == "admin_addres":
            if user_id != ADMIN_ID:
                return
            bot.answer_callback_query(call.id)
            show_materials(chat_id, msg_id, 0, admin_pick_mode=True)

        elif data.startswith("admin_addres_page:"):
            if user_id != ADMIN_ID:
                return
            bot.answer_callback_query(call.id)
            show_materials(chat_id, msg_id, int(data.split(":")[1]), admin_pick_mode=True)

        elif data.startswith("admin_addres_subj:"):
            if user_id != ADMIN_ID:
                return
            bot.answer_callback_query(call.id)
            start_addresource_flow(chat_id, data.split(":", 1)[1])

        else:
            bot.answer_callback_query(call.id)

    except Exception:
        try:
            bot.answer_callback_query(call.id, "حدث خطأ، حاول مجدداً", show_alert=True)
        except Exception:
            pass


if __name__ == "__main__":
    t_flask = threading.Thread(target=run_flask)
    t_flask.daemon = True
    t_flask.start()

    t_ping = threading.Thread(target=keep_alive_ping)
    t_ping.daemon = True
    t_ping.start()

    bot.polling(none_stop=True)
