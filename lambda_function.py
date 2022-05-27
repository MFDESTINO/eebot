import requests
import csv
import json
from io import StringIO
from datetime import date
from telegram import Bot
from mycredentials import TOKEN, SHEET_URL, CHAT_ID

class EEBot:

    def __init__(self, cleaning_sheet_url: str, token: str, chat_id: str):
        self.cleaning_sheet_url = cleaning_sheet_url
        self.telegram_bot = Bot(token=token)
        self.chat_id = chat_id
        self.cleaning_sheet = ''
        self.today_workers = ''


    def get_cleaning_sheet(self) -> None:
        response = requests.get(self.cleaning_sheet_url)
        assert response.status_code == 200, 'Wrong status code'
        csvfile = StringIO(response.content.decode())
        
        csvreader = csv.reader(csvfile)
        res = ''
        for row in csvreader:
            res = res + str(row) + '\n'

        self.cleaning_sheet = res

    def get_today_worker(self) -> None:
        today = date.today().weekday()
        print(today)

    def send_today_workers(self) -> None:
        self.telegram_bot.sendMessage(chat_id=self.chat_id, text=self.cleaning_sheet)


def main() -> None:
    eebot = EEBot(SHEET_URL, TOKEN, CHAT_ID)
    eebot.get_cleaning_sheet()
    eebot.send_today_workers()


def lambda_handler(event, context):
    main()
    return {
        'statusCode': 200,
        'body': json.dumps('Sucess')
    }

