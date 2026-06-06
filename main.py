import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚔️ ماجراجویی", callback_data="adv")],
        [InlineKeyboardButton("🗺️ جهان", callback_data="world")],
        [InlineKeyboardButton("👤 شخصیت", callback_data="char")],
    ])
    await update.message.reply_text(
        "🌟 به الدن رینگ متنی خوش آمدی!\n\nیک گزینه رو انتخاب کن:",
        reply_markup=keyboard
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "adv":
        await query.edit_message_text("⚔️ ماجراجویی - در حال توسعه...")
    elif data == "world":
        await query.edit_message_text("🗺️ جهان - در حال توسعه...")
    elif data == "char":
        await query.edit_message_text("👤 شخصیت - در حال توسعه...")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    print("✅ ربات تست آماده‌ست")
    app.run_polling()

if __name__ == "__main__":
    main()
