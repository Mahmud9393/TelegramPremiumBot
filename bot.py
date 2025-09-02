import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ===================== BOT TOKEN =====================
TOKEN = "8319776106:AAFdXejaCi_GV3zRF7-OfLmYRfMx9kKfrF8"

# ===================== PREMIUM APPS =====================
PREMIUM_APPS = {
    "Telegram Premium": {
        "price": "250 Tk",
        "codes": ["Tp001"],
        "links": ["https://drive.google.com/file/d/1UAs7vWaZgB2Kge1c3qp7v7VknAmd-NfN/view?usp=drive_link"]
    },
    "Truecaller Premium": {
        "price": "200 Tk",
        "codes": ["TC002"],
        "links": ["https://drive.google.com/file/d/1_x-xs-_SmGtZiMjULM24PWNETLgwWh_m/view?usp=drive_link"]
    },
    "imo HD Premium": {
        "price": "200 Tk",
        "codes": ["IM003"],
        "links": ["https://drive.google.com/file/d/1-ZY0506YOJjHlg3iR5rhTSNLAUBjYVwt/view?usp=drive_link"]
    },
    "CapCut Premium": {
        "price": "250 Tk",
        "codes": ["CP004"],
        "links": ["https://drive.google.com/file/d/1McX3XY3VavqMXA2-XnCzICa9kuiy0WrI/view?usp=drive_link"]
    },
    "CamScanner Premium": {
        "price": "150 Tk",
        "codes": ["CM005"],
        "links": ["https://drive.google.com/file/d/1LI_aKIUaUa3ENULueMRmXBa0dAILa_dg/view?usp=drive_link"]
    },
    "Clone App Premium": {
        "price": "250 Tk",
        "codes": ["CP006"],
        "links": ["https://drive.google.com/file/d/1AJY38uLgQ7bESgJYmNZLEbdyqV-2beKI/view?usp=drive_link"]
    },
    "WPS Office Premium": {
        "price": "220 Tk",
        "codes": ["WP007"],
        "links": ["https://drive.google.com/file/d/1TbG_77AD4hwiYh2YPvc7XRzr5niPaLL-/view?usp=drive_link"]
    },
    "YouTube Lite": {
        "price": "100 Tk",
        "codes": ["TL008"],
        "links": ["https://drive.google.com/file/d/1YDxnjW9Ruokq1lffAxrUVmLJamoqYTWB/view?usp=drive_link"]
    },
    "YouTube Premium": {
        "price": "300 Tk",
        "codes": ["YTL02"],
        "note": "2 টা লিংক থেকে 2 টা apps install করুন",
        "links": [
            "https://drive.google.com/file/d/14H73jeLfil4M5K8uCNDdWSJY1GGVhDyB/view?usp=drive_link",
            "https://drive.google.com/file/d/1QLFXXq8Q8JAC2pIkZ237ZzKOoR2cu-DW/view?usp=drive_link"
        ]
    },
    "YouTube Music Premium": {
        "price": "220 Tk",
        "codes": ["YMP01"],
        "links": ["https://drive.google.com/file/d/1WY73gGG-L0KDBWhT-fZKtUduphX4ghR9/view?usp=drive_link"]
    },
    "WiFi Router Manager Premium": {
        "price": "350 Tk",
        "codes": ["WRM009"],
        "links": ["https://drive.google.com/file/d/1hA-2ZsPdF8LA0VRseeiKMmwT7eTkkdmY/view?usp=drive_link"]
    },
}

# ===================== LOCK & SESSION TRACKER =====================
lock = asyncio.Lock()
used_codes = {}  # key: code, value: username/user_id

ADMIN_USERNAME = "Aymansadk"  # Admin username

# ===================== START =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👨‍💻 Admin", callback_data="admin")],
        [InlineKeyboardButton("💎 Premium Apps", callback_data="premium")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome! Choose an option:", reply_markup=reply_markup)

# ===================== MENU HANDLER =====================
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    username = update.effective_user.username

    if query.data == "admin":
        await query.edit_message_text(f"👨‍💻 Contact the admin: @{ADMIN_USERNAME}")
    elif query.data == "premium":
        keyboard = []
        for app_name, data in PREMIUM_APPS.items():
            keyboard.append([InlineKeyboardButton(f"{app_name} ({data['price']})", callback_data=f"buy_{app_name}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("💎 Available Premium Apps:", reply_markup=reply_markup)
    elif query.data == "help":
        await query.edit_message_text("❓ Contact admin for support or instructions.")
    elif query.data.startswith("buy_"):
        app_name = query.data.replace("buy_", "")
        context.user_data["selected_app"] = app_name
        await query.edit_message_text(f"🔑 Enter the unlock code for {app_name}:")

    # Admin override panel (optional)
    elif query.data.startswith("override_"):
        if username != ADMIN_USERNAME:
            await query.edit_message_text("❌ Only admin can use override!")
            return
        code_to_override = query.data.replace("override_", "")
        async with lock:
            if code_to_override in used_codes:
                del used_codes[code_to_override]
                for app in PREMIUM_APPS.values():
                    if code_to_override not in app["codes"]:
                        app["codes"].append(code_to_override)
                        break
                await query.edit_message_text(f"✅ Code `{code_to_override}` has been reactivated!")
            else:
                await query.edit_message_text("❌ This code is not currently used.")

# ===================== CODE HANDLER =====================
async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "selected_app" not in context.user_data:
        await update.message.reply_text("⚠️ Please select an app first by using /start")
        return

    app_name = context.user_data["selected_app"]
    user_code = update.message.text.strip()
    user_id = update.effective_user.id
    username = update.effective_user.username or user_id

    async with lock:
        # Normal code usage
        if user_code in used_codes:
            used_by = used_codes[user_code]
            await update.message.reply_text(f"❌ This code was already used by {used_by}!")
            return

        if user_code in PREMIUM_APPS[app_name]["codes"]:
            PREMIUM_APPS[app_name]["codes"].remove(user_code)
            used_codes[user_code] = username

            links = PREMIUM_APPS[app_name]["links"]
            note = PREMIUM_APPS[app_name].get("note", "")
            link_text = f"{note}\n\n" + "\n".join(links) if note else "\n".join(links)

            msg = await update.message.reply_text(
                f"✅ Correct code!\nHere are your download links:\n{link_text}\n(This message will be deleted in 2.5 minutes)"
            )
            await asyncio.sleep(150)
            try:
                await msg.delete()
            except Exception as e:
                print(f"Failed to delete message: {e}")

            # Add override button for admin
            if username == ADMIN_USERNAME:
                keyboard = [[InlineKeyboardButton(f"Override {user_code}", callback_data=f"override_{user_code}")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text("Admin Override Panel:", reply_markup=reply_markup)
        else:
            await update.message.reply_text("❌ Incorrect code for this app!")

# ===================== MAIN =====================
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code))
    print("🚀 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
