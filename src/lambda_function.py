import os
import json
import requests
import datetime
import asyncio
import json
from pocket_bot import PocketBot
from weather_bot import WeatherBot

POCKET_STATS_CONSUMER_KEY = os.environ['POCKET_CONSUMER_ID']
POCKET_STATS_ACCESS_TOKEN = os.environ['POCKET_ACCESS_TOKEN']
BOT_TOKEN = os.environ['BOT_TOKEN']
MANAGER_CHAT_ID = os.environ['CHAT_ID']
TELEGRAM_WEBHOOK_SECRET_TOKEN = os.environ['TELEGRAM_WEBHOOK_SECRET_TOKEN']
WEATHER_LOCATION = os.environ['WEATHER_LOCATION']


SUPPORTED_COMMANDS_RESPONSE = '''
Hi there {firstname}!
I currently only support these commands:
/pocket - show current pocket progress
/weather - show the current weather and today's forecast
'''


SUPPORTED_COMMANDS = (
    '/pocket',
    '/weather',
    )

    
def send_message(msg):
    res = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", params={'chat_id': MANAGER_CHAT_ID, 'text': msg})
    if res.status_code != 200 or res.json()['ok'] != True:
        raise RuntimeError(f"Got error from telegram: {res.content}")

def check_event_valid(event):
    if event.get('detail-type', None) == 'Scheduled Event':
        return True, None
    if event['rawPath'] != '/telegram-pocket-bot':
        return False, None
    if event['headers'].get('x-telegram-bot-api-secret-token', '') !=  TELEGRAM_WEBHOOK_SECRET_TOKEN:
        print("Invalid telegram request")
        return False, None
    body = json.loads(event['body'])
    if body['message']['text'] not in SUPPORTED_COMMANDS:
        return False, SUPPORTED_COMMANDS_RESPONSE.format(firstname=body['message']['from']['first_name'])
    return True, body['message']['text']
    
async def handle_bots(request):
    if not request:
        send_message("Here is your daily briefing:")
    
    if request in ('/pocket', None):
        bot = PocketBot(POCKET_STATS_CONSUMER_KEY, POCKET_STATS_ACCESS_TOKEN)
        print("Sending pocket message")
        send_message(bot.get_msg(scheduled=request is None))
        print("Sent pocket message")
    
    if request in ('/weather', None):
        bot = WeatherBot(WEATHER_LOCATION)
        print("Sending weather message")
        send_message(await bot.get_msg())
        print("Sent weather message")
    

def lambda_handler(event, context):
    print('Starting handler', event, context)
    valid, res_message = check_event_valid(event)
    if not valid:
        if res_message:
            send_message(res_message)
        return
    
    asyncio.run(handle_bots(res_message))
        
        