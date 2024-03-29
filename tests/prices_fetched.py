import yfinance as yf

def get_watchlist():
    with open ('../watchlist.txt', 'r') as file:
        return [line.rstrip() for line in file]

config = {
        'period': '1d',
        'interval': '15m'
        }

for coin in get_watchlist():
    ticker = yf.Ticker(f'{coin}-USD')
    data = ticker.history(
            period=config['period'],
            interval=config['interval'],
            prepost=True,
            actions=False
            )
    print(data.tail(5))
