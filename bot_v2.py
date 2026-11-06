import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = 7800718555
USERS_SET = set()

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
    sections = {
        "ai": "🤖 AI ASSISTANT\n\nAI system coming soon.",
        "security": "🛡️ CYBERSECURITY\n\nSecurity tools coming soon.",
        "osint": "🔍 OSINT\n\nInformation analysis coming soon.",
        "automation": "⚙️ AUTOMATION\n\nAutomation tools coming soon.",
        "developer": "💻 DEVELOPER TOOLS\n\nDeveloper tools coming soon.",
        "owner": "👑 OWNER PANEL\n\nAdministration system coming soon.",
        "settings": "⚙️ SETTINGS\n\nSettings coming soon."
    }
    if query.data == "home":
        await query.edit_message_text("🐉 ASHENREALM\n\nChoose your destination:", reply_markup=main_menu())
    else:
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
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler('admin', admin_cmd))
    app.add_handler(CommandHandler('contact', contact_cmd))
    app.add_handler(CommandHandler('retry', retry_cmd))
    app.add_handler(CommandHandler('maintenance', maintenance_cmd))
    app.add_handler(CommandHandler('reply', reply_cmd))
    app.add_handler(CallbackQueryHandler(admin_button, pattern="^admin_"))
    app.add_handler(CallbackQueryHandler(buttons, pattern="^(ai|security|osint|automation|developer|owner|settings|home)$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_contact_message))
    print("ASHENREALM V2 IS ONLINE!")
    app.run_polling()

if __name__ == "__main__":
    run()
