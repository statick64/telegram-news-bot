import os
import datetime
import random
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
# NEWS_API_KEY: Final = os.environ.get('NEWS_API_KEY')

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

#handling the different commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_text = (
        "🌟 **Hallo! I am Plutomenace News Bot!** 🌟\n\n"
        "I'm here to keep you informed with the latest news. "
        "Type /help to see all available commands and get started. "
        "Feel free to use /news to fetch headlines or search for news inline!\n\n"
        "Happy reading! 📰😊"
    )
    await update.message.reply_text(start_text)

# Help descriptions
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🌟 **Welcome to the News Bot!** 🌟\n\n"
        "Here are some commands to get you started:\n\n"
        "/start - Welcome message and basic bot instructions.\n"
        "/help - Shows this help message detailing command usage.\n"
        "/custom - Sends a custom message.\n"
        "/news - Fetches and displays the latest news.\n\n"
        "🗂️ **News Categories:**\n"
        "/news business - Latest business news\n"
        "/news entertainment - Entertainment updates\n"
        "/news health - Health-related news\n"
        "/news science - Scientific discoveries\n"
        "/news sports - Sports highlights\n"
        "/news technology - Tech news\n\n"
        "🔍 **Inline News Search:**\n"
        "Type '@bot_username query' to search for news inline."
    )
    await update.message.reply_text(help_text)

# Custom command chat
async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    under_construction_text = (
        "🚧 **Under Construction!** 🚧\n\n"
        "Sorry, the custom feature is still in development. "
        "We're working hard to bring you exciting new features. "
        "Stay tuned for updates! 😊"
    )
    await update.message.reply_text(under_construction_text)

# Fetching News from web
async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = ' '.join(context.args) if context.args else 'latest'
    # tells chat that the bot is fetching the news
    await update.message.reply_text("Fetching the latest news, please wait...") 
    news = fetch_news(query)  # Ensure the query is used in fetching news
    await update.message.reply_text(f"Latest News:\n\n{news}")
    # Simple parsing to separate query and category (if provided)
    # if args:
    #     query = args[0]
    #     if len(args) > 1:
    #         category = args[1]

    # query = ' '.join(context.args) if context.args else 'latest'
    # tells chat that the bot is fetching the news
    # await update.message.reply_text("Fetching the latest news, please wait...") 
    # news = fetch_news(category, query)  # Ensure the query is used in fetching news
    # await update.message.reply_text(f"Latest News:\n\n{news}")

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

    # Time-based greeting
    current_time = datetime.datetime.now().time()
    if current_time < datetime.time(12, 0):
        greeting = 'Good morning'
    elif current_time < datetime.time(17, 0):
        greeting = 'Good afternoon'
    else:
        greeting = 'Good evening'

    if any(keyword in processed for keyword in ['hi', 'hello', 'hey']):
        return f'{greeting}! How can I assist you today? 😊'

    if 'how are you' in processed:
        return 'I am good, thank you for asking! How may I help you today? 😊'

    if 'who are you' in processed:
        return 'I am Plutomenace, your friendly news bot.'

    # Random fun responses
    fun_responses = [
        "I'm feeling fantastic today!",
        "Ask me anything, and I'll do my best to help!",
        "Ready for some news? 📰",
    ]

    if any(keyword in processed for keyword in ['fun', 'joke']):
        return random.choice(fun_responses)

    # Thank you response
    if 'thank you' in processed:
        return 'You\'re welcome! If you have more questions, feel free to ask.'

    # Handling common questions
    if 'what can you do' in processed:
        return 'I can fetch the latest news for you. Try the /news command!'

    # Politeness check
    if any(keyword in processed for keyword in ['please', 'kindly']):
        return 'Thank you for your polite request! How may I assist you? 😊'

    return 'I do not understand what you wrote...'

# A function to get the news 
def fetch_news(query='latest'):
    try:
        # if category.lower() == 'categories':
        #     # Provide a list of available news categories
        #     return "Available news categories: business, entertainment, health, science, sports, technology"

        # if category.lower() not in ['general', 'business', 'entertainment', 'health', 'science', 'sports', 'technology']:
        #     return "Invalid category. Type /news categories to see available categories."
        url = f"https://gnews.io/api/v4/top-headlines?token={GNEWS_API_KEY}&lang=en&q={query}"
        response = requests.get(url)

        # url = f"https://gnews.io/api/v4/top-headlines?{category.lower()}token={GNEWS_API_KEY}&lang=en&q={query}"
        # url = f"https://gnews.io/api/v4/top-headlines?category={category.lower()}&lang=en&country=us&max=10&apikey={GNEWS_API_KEY}"
        # response = requests.get(url)

        if response.status_code == 200:
            print("iuoioi")
            data = response.json()
            articles = data.get('articles', [])

            news_messages = []
            for article in articles[:5]:  # Limit to the top 5 articles
                title = article.get('title', 'No title')
                url = article.get('url', '#')
                news_messages.append(f"{title} - {url}")

            return "\n\n".join(news_messages)
        else:
            logger.error(f"Failed to retrieve news. Status Code: {response.status_code}")
            return "Failed to retrieve news."
    
    except requests.RequestException as e:
        logger.error(f"An error occurred: {e}")
        return "Failed to retrieve news due to an error."

# Comment
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