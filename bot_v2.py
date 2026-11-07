import os
import threading
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OWNER_ID = 7800718555
USERS_SET = set()

# --- Keep Alive for Render Free Web Service ---
class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ASHENREALM V2 IS ONLINE!")
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()
    def log_message(self, format, *args):
        return

def start_keep_alive():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), KeepAliveHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"Keep-Alive server running on port {port}")
# ---------------------------------------------

# --- Groq AI Function - V3 مع حماية ---
def ask_groq(user_message):
    if not GROQ_API_KEY:
        return "❌ مفتاح Groq مازال ما تحطش في Render. روح لـ Environment و زيد GROQ_API_KEY."
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    # قائمة الموديلات - اذا واحد ما خدمش يجرب اللي بعدو
    # هذا هو الدرس اللي تعلمناه: ما نعتمدوش على موديل واحد
    models = [
        "llama-3.3-70b-versatile",
        "llama-3.1-70b-versatile",
        "mixtral-8x7b-32768",
        "gemma2-9b-it"
    ]
    
    last_error = ""
    for model in models:
        try:
            data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "انت مساعد ذكي اسمو ASHENREALM. جاوب بالدارجة الجزائرية البسيطة، و كن مفيد و مختصر. اذا سقساوك تكتب كود، اكتبو و اشرحو ببساطة."},
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.7,
                "max_tokens": 1000
            }
            r = requests.post(url, headers=headers, json=data, timeout=30)
            result = r.json()
            if "choices" in result:
                return result["choices"][0]["message"]["content"]
            else:
                last_error = str(result)
                continue
        except Exception as e:
            last_error = str(e)
            continue
    
    return f"❌ صرا مشكل في كل الموديلات: {last_error}"
# ---------------------------------------------

def main_menu():
    keyboard = [
        [InlineKeyboardButton("🤖 AI Assistant", callback_data="ai")],
        [InlineKeyboardButton("🛡️ Cybersecurity", callback_data="security")],
        [InlineKeyboardButton("🔍 OSINT", callback_data="osint")],
        [InlineKeyboardButton("⚙️ Automation", callback_data="automation")],
        [InlineKeyboardButton("💻 Developer Tools", callback_data="developer")],
        [InlineKeyboardButton("👑 Owner Panel", callback_data="owner")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user:
        USERS_SET.add(update.effective_user.id)
    context.user_data['waiting_ai'] = False
    context.user_data['waiting_contact'] = False
    await update.message.reply_text(
        "🐉 Welcome to ASHENREALM!\n\nYour personal AI and Technology Platform.\n\nChoose your destination:",
        reply_markup=main_menu()
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except Exception:
        pass
    if query.data == "home":
        context.user_data['waiting_ai'] = False
        await query.edit_message_text("🐉 ASHENREALM\n\nChoose your destination:", reply_markup=main_menu())
        return
    if query.data == "ai":
        context.user_data['waiting_ai'] = True
        context.user_data['waiting_contact'] = False
        keyboard = [[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="home")]]
        await query.edit_message_text(
            "🤖 AI ASSISTANT\n\nراني واجد! اكتب سؤالك ضرك، و نجاوبك.\n\nمثال: كيفاش نتعلم بايثون؟",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    sections = {
        "security": "🛡️ CYBERSECURITY\n\nSecurity tools coming soon.",
        "osint": "🔍 OSINT\n\nInformation analysis coming soon.",
        "automation": "⚙️ AUTOMATION\n\nAutomation tools coming soon.",
        "developer": "💻 DEVELOPER TOOLS\n\nDeveloper tools coming soon.",
        "owner": "👑 OWNER PANEL\n\nAdministration system coming soon.",
        "settings": "⚙️ SETTINGS\n\nSettings coming soon."
    }
    text = sections.get(query.data, "Unknown section.")
    keyboard = [[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="home")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_cmd(update, context):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ هذه اللوحة للمطور فقط.")
        return
    maint = context.bot_data.get('maintenance', False)
    text = f"👑 لوحة المالك\n\n👥 عدد المستخدمين: {len(USERS_SET)}\n🛠️ الصيانة: {'مفعلة 🟢' if maint else 'متوقفة 🔴'}\n\nاختر:"
    keyboard = [
        [InlineKeyboardButton("🛠️ تفعيل الصيانة", callback_data="admin_maint_on")],
        [InlineKeyboardButton("✅ ايقاف الصيانة", callback_data="admin_maint_off")],
        [InlineKeyboardButton("👥 عدد المستخدمين", callback_data="admin_users")],
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_button(update, context):
    query = update.callback_query
    await query.answer()
    if query.from_user.id != OWNER_ID:
        await query.edit_message_text("⛔ للمطور فقط.")
        return
    if query.data == "admin_maint_on":
        context.bot_data['maintenance'] = True
        await query.edit_message_text("🛠️ تم تفعيل الصيانة.")
    elif query.data == "admin_maint_off":
        context.bot_data['maintenance'] = False
        await query.edit_message_text("✅ تم ايقاف الصيانة.")
    elif query.data == "admin_users":
        await query.edit_message_text(f"👥 عدد المستخدمين: {len(USERS_SET)}\n\nIDs: {list(USERS_SET)[:20]}")

async def contact_cmd(update, context):
    context.user_data['waiting_contact'] = True
    context.user_data['waiting_ai'] = False
    await update.message.reply_text("📩 تواصل مع المطور\n\nاكتب رسالتك ضرك، و المطور راح يقراها.")

async def handle_contact_message(update, context):
    if update.effective_user.id == OWNER_ID:
        return
    if context.user_data.get('waiting_contact'):
        context.user_data['waiting_contact'] = False
        u = update.effective_user
        USERS_SET.add(u.id)
        msg = f"📩 رسالة جديدة\n\n👤 الاسم: {u.first_name}\n🆔 ID: {u.id}\n👤 يوزر: @{u.username if u.username else 'ماكاش'}\n\n💬 الرسالة:\n{update.message.text}\n\nللرد اكتب:\n/reply {u.id} رسالتك"
        await context.bot.send_message(chat_id=OWNER_ID, text=msg)
        await update.message.reply_text("✅ رسالتك وصلت للمطور.")

async def handle_ai_message(update, context):
    if not context.user_data.get('waiting_ai'):
        return
    await update.message.reply_text("⏳ راني نخمم...")
    answer = ask_groq(update.message.text)
    keyboard = [[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="home")]]
    await update.message.reply_text(answer, reply_markup=InlineKeyboardMarkup(keyboard))

async def reply_cmd(update, context):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ للمطور فقط.")
        return
    if len(context.args) < 2:
        await update.message.reply_text("استعمل: /reply <ID> <رسالتك>")
        return
    try:
        tid = int(context.args[0])
        txt = " ".join(context.args[1:])
        await context.bot.send_message(chat_id=tid, text=f"📩 رد من المطور:\n\n{txt}")
        await update.message.reply_text("✅ تم ارسال الرد.")
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {e}")

async def retry_cmd(update, context):
    await update.message.reply_text("🔄 اعادة المحاولة\n\nاوكي، عاودنا من جديد. اكتب /start")

async def maintenance_cmd(update, context):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ هذا الأمر للمطور فقط.")
        return
    if context.args and context.args[0] == "on":
        context.bot_data['maintenance'] = True
        await update.message.reply_text("🛠️ تم تفعيل وضع الصيانة.")
    elif context.args and context.args[0] == "off":
        context.bot_data['maintenance'] = False
        await update.message.reply_text("✅ تم إيقاف وضع الصيانة.")
    else:
        await update.message.reply_text("استعمل: /maintenance on  أو  /maintenance off")

def run():
    if not TOKEN:
        print("ERROR: BOT_TOKEN is missing!")
        return
    start_keep_alive()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler('admin', admin_cmd))
    app.add_handler(CommandHandler('contact', contact_cmd))
    app.add_handler(CommandHandler('retry', retry_cmd))
    app.add_handler(CommandHandler('maintenance', maintenance_cmd))
    app.add_handler(CommandHandler('reply', reply_cmd))
    app.add_handler(CallbackQueryHandler(admin_button, pattern="^admin_"))
    app.add_handler(CallbackQueryHandler(buttons, pattern="^(ai|security|osint|automation|developer|owner|settings|home)$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ai_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_contact_message))
    print("ASHENREALM V2 IS ONLINE!")
    app.run_polling()

if __name__ == "__main__":
    run()
