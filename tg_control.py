# tg_control.py

from telegram import Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
import api_config
import threading
import subprocess
import threading
import json
import logging
import datetime
import shlex
import re
from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# This will hold the reference to the thread
bot_thread = None
# This will hold the reference to the process
bot_process = None
# This will hold the best parameters
best_params = None

async def start_live(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start_live is issued."""
    global bot_thread, bot_process
    if bot_thread is None:
        bot_thread = threading.Thread(target=start_bot)
        bot_thread.start()
        await update.message.reply_text('Bot started')
    else:
        await update.message.reply_text('Bot is already running')

async def stop_live(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /stop_live is issued."""
    global bot_thread, bot_process
    if bot_thread is not None:        
        stop_bot(bot_process)
        bot_thread.join()  # Wait for the bot to stop
        bot_thread = None
        bot_process = None
        await update.message.reply_text('Bot stopped')
    else:
        await update.message.reply_text('Bot is not running')

def start_bot():
    global bot_process
    try:
        # Run your live_trading.py script 
        bot_process = subprocess.Popen([".venv\Scripts\python.exe", "live_trading.py"])
    except Exception as e:
        # Handle exceptions here
        print(f"An error occurred: {e}")

def stop_bot(bot_process):
    # Implement a way to stop the bot
    if bot_process is not None:
        bot_process.terminate()

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /status is issued."""
    global bot_thread
    if bot_thread is not None:       
        await update.message.reply_text('Bot is running')
    else:
        await update.message.reply_text('Bot is not running')

def run_optimizer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /run_optimizer is issued."""
    update.message.reply_text('Optimizer started')
    # Start a new thread to run the optimizer
    threading.Thread(target=run_optimizer_in_background, args=(update, context)).start()

def run_optimizer_in_background(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /run_optimizer is issued."""
    global best_params  # Declare best_params as global
    # Implement the functionality to start the optimizer here
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=30)  # change to 15 for 15 days

    # Run your main.py script with use_optimization flag and dates
    command = f".venv\Scripts\python.exe main.py --use_optimization --start_date {start_date} --end_date {end_date}"
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    # Extract the best parameters from the output
    # This depends on how your script outputs the best parameters, adjust the regex accordingly
    match = re.search(r"Best parameters: (.*)", stdout.decode())
    if match:
        best_params = match.group(1)  # Now this will update the global variable
        update.message.reply_text('Optimizer finished, best parameters found')
        keyboard = [[InlineKeyboardButton("Yes", callback_data='yes'),
                     InlineKeyboardButton("No", callback_data='no')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Do you want to use these parameters for live trading?', reply_markup=reply_markup)
    else:
        update.message.reply_text('Optimizer finished, but no best parameters found')

def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global best_params  # Declare best_params as global
    query = update.callback_query
    query.answer()
    if query.data == 'yes':
        # Run your live_trading.py script with the best parameters
        command = f".venv\Scripts\python.exe live_trading.py --params {best_params}"
        bot_process = subprocess.Popen(shlex.split(command))
        query.edit_message_text(text="Live trading started with new parameters")
    else:
        query.edit_message_text(text="Live trading will continue with the previous parameters")

def main() -> None:
    """Start the bot."""
    application = Application.builder().token(api_config.TG_BOT_API).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start_live", start_live))
    application.add_handler(CommandHandler("stop_live", stop_live))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("run_optimizer", run_optimizer))
    application.add_handler(CallbackQueryHandler(button))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
