"""
Telegram Bot Handler - Receives messages and sends responses
This allows the bot to be interactive and respond to user commands
"""

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from database import get_lowest_price

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    message = """
👋 <b>Welcome to Ryanair Price Tracker Bot!</b>

I'm tracking flights for you:
✈️ <b>Route:</b> TLL → BER (Tallinn to Berlin)
📅 <b>Dates:</b> June 9, 10, 12, 2026
💰 <b>Thresholds:</b> €40, €35, €30

<b>Commands:</b>
/start - Show this message
/price - Get latest price updates
/status - Bot status
/help - Help information

I'll send you:
📱 Telegram updates every 15 minutes
📧 Email when prices drop below thresholds
"""
    await update.message.reply_text(message, parse_mode='HTML')
    logger.info(f"User {update.effective_user.id} sent /start")


async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /price command - show latest prices"""
    try:
        price_stats = get_lowest_price(1)  # Today's prices
        
        if price_stats:
            lowest, highest, average, count = price_stats
            message = f"""
📊 <b>Latest Price Data</b>

💰 <b>Lowest:</b> €{lowest:.2f}
💸 <b>Highest:</b> €{highest:.2f}
📈 <b>Average:</b> €{average:.2f}

✈️ <b>Flights checked:</b> {count}

<i>Data from last check</i>
"""
        else:
            message = "No price data available yet. The bot will start sending updates soon!"
        
        await update.message.reply_text(message, parse_mode='HTML')
        logger.info(f"User {update.effective_user.id} requested /price")
        
    except Exception as e:
        logger.error(f"Error in /price command: {e}")
        await update.message.reply_text("❌ Error retrieving price data", parse_mode='HTML')


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command - show bot status"""
    message = """
✅ <b>Bot Status: ACTIVE</b>

🚀 <b>Status:</b> Running on Railway
📡 <b>Check Interval:</b> Every 15 minutes
🗓️ <b>Tracking:</b> TLL → BER (June 9, 10, 12)

<b>Notifications:</b>
📱 Telegram: Every 15 minutes
📧 Email: When price crosses thresholds

Last check: Running automatically
"""
    await update.message.reply_text(message, parse_mode='HTML')
    logger.info(f"User {update.effective_user.id} requested /status")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    message = """
📚 <b>Help & Information</b>

<b>I'm tracking Ryanair flights from Tallinn (TLL) to Berlin (BER) on:</b>
• June 9, 2026
• June 10, 2026
• June 12, 2026

<b>How it works:</b>
1️⃣ I check prices every 15 minutes
2️⃣ I send you Telegram updates every 15 minutes
3️⃣ I send email alerts when price drops:
   • Below €40 → Email alert
   • Below €35 → Email alert
   • Below €30 → Email alert

<b>Your notifications are set to:</b>
📧 Email: eshan2304parmar@gmail.com
📱 Telegram: This chat

<b>Questions?</b>
Use /price to see latest prices
Use /status to check bot status
"""
    await update.message.reply_text(message, parse_mode='HTML')
    logger.info(f"User {update.effective_user.id} requested /help")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages"""
    text = update.message.text.lower()
    
    if 'price' in text:
        await price_command(update, context)
    elif 'status' in text:
        await status_command(update, context)
    elif 'help' in text:
        await help_command(update, context)
    else:
        message = """
I didn't understand that command. Try:
/price - Get latest prices
/status - Bot status
/help - Help information
/start - Welcome message
"""
        await update.message.reply_text(message)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")


def start_telegram_bot_handler():
    """Start the Telegram bot handler (polling mode)"""
    
    if not TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN not set!")
        return None
    
    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("price", price_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Add message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start polling
    logger.info("🤖 Starting Telegram bot handler (polling mode)...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    logger.info("Starting Telegram bot handler...")
    start_telegram_bot_handler()
