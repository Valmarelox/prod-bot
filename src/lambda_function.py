import os
import json
from typing import List
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

def is_event_scheduled(event) -> bool:
    return event.get('detail-type', None) == 'Scheduled Event'

class TelegramBot:
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
    
    def send_message(self, msg: str):
        res = requests.get(f"https://api.telegram.org/bot{self.token}/sendMessage", params={'chat_id': self.chat_id, 'text': msg})
        if res.status_code != 200 or res.json()['ok'] != True:
            raise RuntimeError(f"Got error from telegram: {res.content!r}")

    def check_event_valid(self, event) -> bool:
        if is_event_scheduled(event):
            return True
        if event['rawPath'] != '/telegram-pocket-bot':
            return False
        if event['headers'].get('x-telegram-bot-api-secret-token', '') !=  TELEGRAM_WEBHOOK_SECRET_TOKEN:
            print("Invalid telegram request")
            return False
        return True
        
    def get_response_type(self, event) -> List[str]:
        body = json.loads(event['body'])
        if body['message']['text'] not in SUPPORTED_COMMANDS:
            self.send_message(SUPPORTED_COMMANDS_RESPONSE.format(firstname=body['message']['from']['first_name']))
            return []
        return body['message']['text']

    async def handle_bots(self, event):
        bots = []
        is_scheduled = is_event_scheduled(event)
        if is_scheduled:
            self.send_message("Here is your daily briefing:")
            requests = SUPPORTED_COMMANDS
        else: 
            requests = [self.get_response_type(event)]
        
        if '/pocket' in requests:
            bots.append(PocketBot(POCKET_STATS_CONSUMER_KEY, POCKET_STATS_ACCESS_TOKEN))
        
        if '/weather' in requests:
            bots.append(WeatherBot(WEATHER_LOCATION))
            
        msgs = await asyncio.gather(*[bot.get_msg(is_scheduled) for bot in bots])
        print(msgs)
        for msg in msgs:
            self.send_message(msg)

def lambda_handler(event, context):
    print('Starting handler', event, context)
    bot = TelegramBot(token=BOT_TOKEN, chat_id=MANAGER_CHAT_ID)
    if not bot.check_event_valid(event):
        return
    
    asyncio.run(bot.handle_bots(event))
        
        