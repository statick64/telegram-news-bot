import os
from dotenv import load_dotenv
import requests
from typing import Final
import logging  # Import the logging module

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.ext import InlineQueryHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent

# Load environment variables from .env file
load_dotenv()

# Securely fetch your tokens and keys from the environment variable
TOKEN: Final = os.environ.get('TOKEN')
BOT_USERNAME: Final = os.environ.get('BOT_USERNAME')
GNEWS_API_KEY: Final = os.environ.get('GNEWS_API_KEY')

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

#handling the different commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Welcome! Type /help to get started.')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "/start - Welcome message and basic bot instructions.\n"
        "/help - Shows this help message detailing command usage.\n"
        "/custom - Sends a custom message.\n"
        "/news - Fetches and displays the latest news.\n"
    )
    await update.message.reply_text(help_text)

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This is a custom message')

async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = ' '.join(context.args) if context.args else 'latest'
    # tells chat that the bot is fetching the news
    await update.message.reply_text("Fetching the latest news, please wait...") 
    news = fetch_news(query)  # Ensure the query is used in fetching news
    await update.message.reply_text(f"Latest News:\n\n{news}")

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    results = [
        InlineQueryResultArticle(
            id=query,
            title="Latest News",
            input_message_content=InputTextMessageContent(fetch_news(query))
        )
    ]
    await update.inline_query.answer(results)

# Handles response 
def handle_response(text: str) -> str:
    processed: str = text.lower()
    
    if 'how are you' in processed:
        return 'I am good'
    
    if 'who are you' in processed:
        return 'I am plutomenace'
    
    return 'I do not understand what you wrote...'

# A function to get the news 
def fetch_news(query='latest'):
    try:
        url = f"https://gnews.io/api/v4/top-headlines?token={GNEWS_API_KEY}&lang=en&q={query}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            
            news_messages = []
            for article in articles[:5]:  # Limit to the top 5 articles
                title = article.get('title', 'No title')
                url = article.get('url', '#')
                news_messages.append(f"{title} - {url}")
            
            return "\n\n".join(news_messages)
        else:
            logger.error(f"Failed to retrieve news. Status Code: {response.status_code}")  # logs news error
            return "Failed to retrieve news."
    # Error handling for the news 
    except requests.RequestException as e:
        logger.error(f"An error occurred: {e}")
        return "Failed to retrieve news due to an error."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    logger.info(f'User ({update.message.chat.id}) in {message_type}: "{text}"') # Logs the chat chat type, Group/private

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)
    
    logger.info('Bot: ' + response)
    await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f'Update {update} caused error {context.error}')

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(CommandHandler('news', news_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(InlineQueryHandler(inline_query))
    app.add_error_handler(error)

    logger.info('Bot is polling...')
    app.run_polling(poll_interval=3)
