import os
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "I am alive!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# আপনার তথ্য
ADMIN_ID = 7291899180  
BOT_TOKEN = "8612046126:AAE8MIpqGR-Ha4YH7PfiQVw_t33Fv3hLYQ4" 

user_data_storage = {} 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ফাইল রিসিভ করার জন্য প্রস্তুত। আপনার ফাইল পাঠান।")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document
    # শুধুমাত্র এক্সেল ফাইল চেক করা হচ্ছে
    if file.file_name.lower().endswith(('.xlsx', '.xls', '.csv')):
        user_id = update.effective_user.id
        user_data_storage[user_id] = {'file_id': file.file_id, 'file_name': file.file_name}
        
        # এখানে সোজাসুজি বাটন তৈরি করা হয়েছে
        keyboard = [[InlineKeyboardButton("বিকাশ", callback_data='বিকাশ'),
                     InlineKeyboardButton("নগদ", callback_data='নগদ')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text("আপনার ফাইলটি পাওয়া গেছে। মাধ্যম সিলেক্ট করুন:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("দয়া করে শুধুমাত্র এক্সেল ফাইল পাঠান।")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if user_id in user_data_storage:
        user_data_storage[user_id]['method'] = query.data
        # বাটন ক্লিক করলে নম্বর চাবে
        await query.edit_message_text(text=f"আপনার {query.data} নম্বরটি দিন।")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # ইউজার নম্বর পাঠানোর পর কাজ শুরু হবে
    if user_id in user_data_storage and 'method' in user_data_storage[user_id]:
        data = user_data_storage[user_id]
        number = update.message.text
        
        await update.message.reply_text(f"আপনার {data['method']} নম্বর এবং ফাইল অ্যাডমিনের কাছে পাঠানো হয়েছে।")

        # এই অংশটি আপনার (ADMIN_ID) ইনবক্সে ফাইল পাঠিয়ে দিবে
        caption = f"🚀 নতুন ফাইল!\n👤 নাম: {update.effective_user.full_name}\n💰 মাধ্যম: {data['method']}\n📱 নম্বর: {number}"
        await context.bot.send_document(chat_id=ADMIN_ID, document=data['file_id'], caption=caption)
        
        # ডাটা মুছে ফেলা
        del user_data_storage[user_id]

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))
    
    print("বট চলছে... শুধু ফাইল পাঠান।")
    app.run_polling()
