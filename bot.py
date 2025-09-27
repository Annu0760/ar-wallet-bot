import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import sqlite3
import os

# Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN", "7983263845:AAH0dJNALIZJu24sJPySVKZ0Wr9JXlSH06c")

# Microworkers Links
MICROWORKERS_LINK = "https://www.microworkers.com"
TASK1_LINK = "https://www.microworkers.com/campaign_details.php?campaign_id=EXAMPLE1"
TASK2_LINK = "https://www.microworkers.com/campaign_details.php?campaign_id=EXAMPLE2"
TASK3_LINK = "https://www.microworkers.com/campaign_details.php?campaign_id=EXAMPLE3"

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, username TEXT, balance REAL, 
                 tasks_completed INTEGER, total_earned REAL)''')
    conn.commit()
    conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.first_name
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username, balance, tasks_completed, total_earned) VALUES (?, ?, 0, 0, 0)", 
              (user_id, username))
    conn.commit()
    conn.close()
    
    keyboard = [
        [InlineKeyboardButton("👷 Microworkers Tasks", callback_data="tasks")],
        [InlineKeyboardButton("💰 My Balance", callback_data="balance")],
        [InlineKeyboardButton("🎯 Withdraw Money", callback_data="withdraw")],
        [InlineKeyboardButton("📞 Support", callback_data="support")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"👋 Welcome to Microworkers Earning Bot! 🚀\n\n"
        f"Hi {username}! Start earning with simple tasks:\n\n"
        "✅ Microworkers Verified Tasks\n"
        "✅ Instant Payments\n" 
        "✅ 24/7 Support\n\n"
        "Click Microworkers Tasks to start earning!",
        reply_markup=reply_markup
    )

async def show_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📱 App Install - ₹80", url=TASK1_LINK)],
        [InlineKeyboardButton("📺 YouTube Subscribe - ₹50", url=TASK2_LINK)],
        [InlineKeyboardButton("🌐 Website Visit - ₹30", url=TASK3_LINK)],
        [InlineKeyboardButton("👷 More Microworkers Tasks", url=MICROWORKERS_LINK)],
        [InlineKeyboardButton("✅ Task Completed", callback_data="task_done")],
        [InlineKeyboardButton("↩️ Main Menu", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🎯 Available Microworkers Tasks:\n\n"
        "1. App Install - ₹80 per app 📱\n"
        "2. YouTube Subscribe - ₹50 per channel 📺\n" 
        "3. Website Visit - ₹30 per visit 🌐\n\n"
        "How to earn:\n"
        "• Click any task button\n"
        "• Complete the task on Microworkers\n"
        "• Click 'Task Completed' for payment\n"
        "• Minimum withdrawal: ₹100 💰",
        reply_markup=reply_markup
    )

async def task_completed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    username = query.from_user.first_name
    
    task_earning = 50
    user_share = task_earning * 0.9
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance + ?, tasks_completed = tasks_completed + 1, total_earned = total_earned + ? WHERE user_id = ?", 
              (user_share, task_earning, user_id))
    conn.commit()
    conn.close()
    
    keyboard = [[InlineKeyboardButton("📋 More Tasks", callback_data="tasks")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"✅ Task Completed Successfully! 🎉\n\n"
        f"User: {username}\n"
        f"Earned: ₹{user_share} (90% of task value)\n"
        f"Admin Share: ₹{task_earning * 0.1} (10%)\n\n"
        f"Contact Support: @Ramzanali56\n\n"
        f"Keep completing tasks to earn more! 👇",
        reply_markup=reply_markup
    )

async def check_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT balance, tasks_completed, total_earned FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    
    balance = result[0] if result else 0
    tasks_done = result[1] if result else 0
    total_earned = result[2] if result else 0
    
    keyboard = [
        [InlineKeyboardButton("📋 Earn More", callback_data="tasks")],
        [InlineKeyboardButton("💳 Withdraw", callback_data="withdraw")],
        [InlineKeyboardButton("↩️ Main Menu", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"💰 Your Earnings Summary:\n\n"
        f"Current Balance: ₹{balance}\n"
        f"Tasks Completed: {tasks_done}\n"
        f"Total Earned: ₹{total_earned}\n"
        f"Minimum Withdrawal: ₹100\n\n"
        f"90% of all earnings go to you! 🚀",
        reply_markup=reply_markup
    )

def main():
    init_db()
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(show_tasks, pattern="^tasks$"))
    application.add_handler(CallbackQueryHandler(task_completed, pattern="^task_done$"))
    application.add_handler(CallbackQueryHandler(check_balance, pattern="^balance$"))
    application.add_handler(CallbackQueryHandler(start, pattern="^main_menu$"))
    
    print("🚀 Microworkers Bot Started Successfully!")
    application.run_polling()

if __name__ == '__main__':
    main()