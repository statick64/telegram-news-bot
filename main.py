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
WEATHER_API_KEY: Final = os.getenv('WEATHER_API_KEY')

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

#handling the different commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_text = (
        "🌟 Hallo! I am Southsider News Bot! 🌟\n\n"
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
        "/news - Fetches and displays the latest news.\n"
        "/weather - Fetches and displays the current weather conditions for a specified city.\n\n"
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
    await update.message.reply_text(help_text, parse_mode=None)


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
        return 'I am Southsider, your friendly news bot.'

    # Dynamic Fun Responses
    fun_responses = [
        "I'm feeling fantastic today!",
        "Exploring the latest news with a touch of excitement!",
        "Get ready for a news adventure! 🌍🚀",
        "Breaking news: It's a great day!",
        "Unveiling the day's top stories with a smile! 😃📰",
    ]

    trigger_keywords = ['fun', 'news', 'gossip']

    if any(keyword in processed for keyword in trigger_keywords):
        return random.choice(fun_responses)

    # Thank you response
    if 'thank you' in processed:
        return 'You\'re welcome! If you have more questions, feel free to ask.'
    
    # Example user assistance including /help command
    if 'help' in processed or 'need assistance' in processed:
        return 'Of course! I\'m here to /help. What do you need assistance with? You can ask about news, specific topics, or use commands like /weather or /custom.'

    # Handling common questions
    if 'what can you do' in processed:
        return 'I can fetch the latest news for you. Try the /news command!'
    
    # Example educational response
    if 'how do you work' in processed:
        return 'I analyze your questions and fetch relevant news articles. Feel free to ask anything!'
    
    # Example user engagement
    if 'recommend' in processed:
        return 'Certainly! What type of news are you interested in? Technology, sports, or something else?'

    # Politeness check
    if any(keyword in processed for keyword in ['please', 'kindly']):
        return 'Thank you for your polite request! How may I assist you? 😊'
    
    # Improved Unrecognized Input Response
    unrecognized_response = [
        "Oops! It seems like I didn't catch that. Could you please rephrase your question?",
        "I'm sorry, I didn't quite get that. Could you try asking in a different way?",
        "My circuits might be a bit tangled! Can you help me understand your question better?",
    ]

    return random.choice(unrecognized_response)

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

# Modify the function to fetch weather
async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = ' '.join(context.args)  # Extract city from command arguments
    if not city:
        await update.message.reply_text("Please specify a city. Example: /weather London")
        return

    # Fetch weather data using the API
    weather_data = fetch_weather(city)

    # Send the weather information as a reply
    await update.message.reply_text(weather_data)

# Fetching the weather report
def fetch_weather(city):
    try:
        url = f'http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}&aqi=no'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            # Extract relevant weather information from the response
            temperature = data['current']['temp_c']
            weather_description = data['current']['condition']['text']

            return f"Current weather in {city}: {weather_description}, Temperature: {temperature}°C"
        else:
            return f"Failed to retrieve weather information. Error: {response.text}"

    except requests.RequestException as e:
        return f"Failed to retrieve weather information due to an error: {e}"


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
    app.add_handler(CommandHandler('weather', weather_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(InlineQueryHandler(inline_query))
    app.add_error_handler(error)

    logger.info('Bot is polling...')
    app.run_polling(poll_interval=3)