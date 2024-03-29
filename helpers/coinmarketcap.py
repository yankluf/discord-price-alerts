import os, json, requests

class CoinMktCapConfig:
    def __init__(self):
        self.api_key = os.getenv('COINMARKETCAP_API_KEY')
        self.endpoint = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        self.headers = {
                'Accept': 'application/json',
                'X-CMC_PRO_API_KEY': self.api_key
                }
        self.params = {
                'start': '1',
                'limit': '200',
                'convert': 'USD'
                }

class PricesRequest:
    def __init__(self, coinlist):
        self.config = CoinMktCapConfig()
        self.data = self.fetch_prices()
        self.index = self.create_index(coinlist)
        self.prices = self.get_prices()

    def fetch_prices(self):
        r = requests.get(
                url = self.config.endpoint,
                headers = self.config.headers,
                params = self.config.params
                )
        return r.json()['data']

    def create_index(self, coinlist):
        return [(coin['symbol'], index) for index, coin in enumerate(self.data) if coin['symbol'] in coinlist]

    def get_prices(self):
        prices = {}
        for coin in self.index:
            symbol = coin[0]
            index = coin[1]
            coin_info = self.data[index]['quote']['USD']
            prices[symbol] = {
                    'price': coin_info['price'],
                    'volume_24h': coin_info['volume_24h'], 
                    'change_1h': coin_info['percent_change_1h'], 
                    'change_24h': coin_info['percent_change_24h'], 
                    'change_7d': coin_info['percent_change_7d'], 
                    'last_update': self.data[index]['last_updated']
                    }
        return prices
