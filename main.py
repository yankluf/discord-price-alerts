import os, datetime, time, warnings
import json, requests
from emoji import emojize as emoji
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()
warnings.simplefilter(action='ignore', category=FutureWarning)

class Config:
    def __init__(self):
        self.base_url = os.getenv('DISCORD_API_BASE_URL')
        self.channel = os.getenv('DISCORD_CHANNEL_ID')
        self.endpoint = f'{self.base_url}/channels/{self.channel}/messages'
        self.auth_header = f"Bot {os.getenv('DISCORD_BOT_TOKEN')}"
        self.headers = {
            'Authorization': self.auth_header,
            'User-Agent': 'DiscordBot',
            'Content-Type': 'application/json'
            }

class App:
    def __init__(self):
        self.config = Config()
        self.watchlist = self.read_watchlist()
        self.last_check = self.check_prices()
        self.formatted_message = self.format_message()

    def read_watchlist(self):
        with open('watchlist.txt', 'r') as file:
            return [line.rstrip() for line in file]

    def check_prices(self):
        prices = []
        for coin in self.watchlist:
            ticker = yf.Ticker(f'{coin}-USD')
            data_1day = ticker.history(period='1d', interval='30m', prepost=True, actions=False)

            data_30m = data_1day.tail(2)['Close']
            movement_30m = (data_30m.iloc[1] - data_30m.iloc[0]) / data_30m.iloc[0] * 100

            data_2h = data_1day.tail(4)['Close']
            movement_2h = (data_2h.iloc[3] - data_2h.iloc[0]) / data_2h.iloc[0] * 100

            data_4h = data_1day.tail(8)['Close']
            movement_4h = (data_4h.iloc[7] - data_4h.iloc[0]) / data_4h.iloc[0] * 100

            #This will go in format_message()
            info = {
                'ticker': coin,
                'current_price': f'{data_30m.iloc[1]:.2f}',
                'price_differences': {
                    '30min': f'{movement_30m:+.2f} %',
                    '2h': f'{movement_2h:+.2f} %',
                    '4h': f'{movement_4h:+.2f} %'
                    }
                }

            prices.append(info)

        return prices

    def format_message(self):
        formatted = []
        for coin in self.last_check:
          info = f'''
{emoji(':play_button:')} **{coin['ticker']}:** {coin['current_price']}
- 30 min: {coin['price_differences']['30min']}
- 2 horas: {coin['price_differences']['2h']}
- 4 horas: {coin['price_differences']['4h']}'''
          formatted.append(info)
        
        output = '\n'.join(formatted)
        return output



    def send_alert(self):
        payload = {
            'embeds': [{
                'title': emoji(':point_up_2: ') + datetime.datetime.now().strftime('%d %B %y @ %H:%M (Hora Central US)'),
                'type': 'rich',
            }],
            'content': self.formatted_message
        }

        r = requests.post(
            url = self.config.endpoint,
            headers = self.config.headers,
            data=json.dumps(payload)
            )
        
        return r.json()

if __name__ == '__main__':
    while True:
        app = App()
        app.format_message()
        app.send_alert()
        del app
        time.sleep(7200)
        continue
    
