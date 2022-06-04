import requests
import csv
import json
from io import StringIO
from datetime import datetime, timedelta
from telegram import Bot
from mycredentials import TOKEN, SHEET_URL, CHAT_ID

PLACES = ['Sala', 'Cozinha', 'Banheiro Social', 'Suite']

class EEBot:

    def __init__(self, cleaning_sheet_url: str, token: str, chat_id: str) -> None:
        self.cleaning_sheet_url = cleaning_sheet_url
        self.telegram_bot = Bot(token=token)
        self.today = datetime.now() + timedelta(hours=-3) #GMT-3
        self.chat_id = chat_id
        self.cleaning_sheet = []
        self.today_place_workers = {}
        self.today_trash_n_dishes = []
        self.today_message = ''


    def get_cleaning_sheet(self) -> None:
        response = requests.get(self.cleaning_sheet_url)
        assert response.status_code == 200, 'Wrong status code'
        csvfile = StringIO(response.content.decode())
        
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            self.cleaning_sheet.append(row)

    def get_week_cycle(self) -> int:
        alpha = datetime(year=2022, month=5, day=28)
        omega = self.today
        week_cycle = int((omega - alpha).days/7)%3
        return week_cycle

    def get_today_place_workers(self) -> None:
        week_cycle = self.get_week_cycle()
        place_workers = self.cleaning_sheet[week_cycle+2][0:4]
        for i in range(4):
            self.today_place_workers[PLACES[i]] = place_workers[i]
    
    def get_today_trash_n_dishes(self) -> None:
        weekday = self.today.weekday()
        if weekday  in [0, 2, 4]:
            self.today_trash_n_dishes = [self.cleaning_sheet[2][int(weekday /2)+5], 
                                         self.cleaning_sheet[3][int(weekday /2)+5]]

    def make_today_message(self) -> None:
        message = "Escala de hoje ({}/{}):\n\n".format(self.today.day, self.today.month)
        if self.today_trash_n_dishes:
            message += "Tirar lixo e guardar louça:\n{} e {}\n\n".format(*self.today_trash_n_dishes)
        else:
            message += "Ninguém tira o lixo nem guarda louça hoje :(\n\n"
        first_weekday = self.today - timedelta(days=(self.today.weekday()+2)%7)
        last_weekday = self.today - timedelta(days=(self.today.weekday()+2)%7-6)
        message += "Escala semanal ({}/{} - {}/{}):\n\n".format(first_weekday.day, first_weekday.month,
                                                                last_weekday.day, last_weekday.month)
        places = self.today_place_workers.keys()
        for place in places:
            message += "{}: {}\n".format(place, self.today_place_workers[place])
        self.today_message=message


    def send_today_message(self) -> None:
        self.telegram_bot.sendMessage(chat_id=self.chat_id, text=self.today_message)


def main() -> None:
    eebot = EEBot(SHEET_URL, TOKEN, CHAT_ID)
    eebot.get_cleaning_sheet()
    eebot.get_today_place_workers()
    eebot.get_today_trash_n_dishes()
    eebot.make_today_message()
    eebot.send_today_message()


def lambda_handler(event, context):
    main()
    return {
        'statusCode': 200,
        'body': json.dumps('Sucess')
    }

if __name__ == "__main__":
    main()