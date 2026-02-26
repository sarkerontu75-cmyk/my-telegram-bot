import os
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Flask সার্ভার সেটআপ (বটকে সজাগ রাখার জন্য)
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

# --- বটের মূল কোড ---

# আপনার তথ্য (এখানে ক্রেতার আইডি বসিয়ে দিলেই হবে)
ADMIN_ID =  7291899180
BOT_TOKEN = "8612046126:AAE8MIpqGR-Ha4YH7PfiQVw_t33Fv3hLYQ4" 

user_data_storage = {} 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ফাইল রিসিভ করার জন্য প্রস্তুত। আপনার ফাইল পাঠান।")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document
    if file.file_name.lower().endswith(('.xlsx', '.xls', '.csv')):
        user_id = update.effective_user.id
        user_data_storage[user_id] = {'file_id': file.file_id, 'file_name': file.file_name}
        
        # পেমেন্ট মেথড বাটন (বাইনান্স যুক্ত করা হয়েছে)
        keyboard = [
            [InlineKeyboardButton("বিকাশ", callback_data='বিকাশ'),
             InlineKeyboardButton("নগদ", callback_data='নগদ')],
            [InlineKeyboardButton("বাইনান্স (Binance)", callback_data='বাইনান্স')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("আপনার ফাইলটি পাওয়া গেছে। পেমেন্ট মাধ্যম সিলেক্ট করুন:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("দয়া করে শুধুমাত্র এক্সেল ফাইল পাঠান।")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # অ্যাডমিন যদি 'রিসিভ' বাটনে ক্লিক করে
    if query.data.startswith('received_'):
        target_user_id = query.data.split('_')[1]
        try:
            await context.bot.send_message(chat_id=target_user_id, text="✅ আপনার ফাইলটি অ্যাডমিন রিসিভ করেছে।")
            await query.edit_message_caption(caption=query.message.caption + "\n\n✅ Status: Received")
        except:
            await query.edit_message_caption(caption=query.message.caption + "\n\n❌ ইউজারকে মেসেজ পাঠানো যায়নি।")
        return

    # ইউজার যদি পেমেন্ট মেথড সিলেক্ট করে
    if user_id in user_data_storage:
        user_data_storage[user_id]['method'] = query.data
        await query.edit_message_text(text=f"আপনার {query.data} নম্বর/আইডিটি দিন।")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_data_storage and 'method' in user_data_storage[user_id]:
        data = user_data_storage[user_id]
        number = update.message.text
        
        await update.message.reply_text(f"আপনার {data['method']} তথ্য এবং ফাইল অ্যাডমিনের কাছে পাঠানো হয়েছে।")

        # অ্যাডমিনের কাছে ফাইল পাঠানো (সাথে রিসিভ বাটন)
        caption = f"🚀 নতুন ফাইল!\n👤 নাম: {update.effective_user.full_name}\n🆔 ইউজার আইডি: {user_id}\n💰 মাধ্যম: {data['method']}\n📱 নম্বর/আইডি: {number}"
        
        admin_keyboard = [[InlineKeyboardButton("✅ Receive", callback_data=f'received_{user_id}')]]
        admin_markup = InlineKeyboardMarkup(admin_keyboard)

        await context.bot.send_document(
            chat_id=ADMIN_ID, 
            document=data['file_id'], 
            caption=caption,
            reply_markup=admin_markup
        )
        
        del user_data_storage[user_id]

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(CallbackQueryHandler(button_click))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))
    
    print("বট চলছে...")
    application.run_polling()
