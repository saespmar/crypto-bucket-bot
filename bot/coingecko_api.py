import requests


class CoinGeckoRequester:

    url_v3 = 'https://api.coingecko.com/api/v3/'
    commonCurrencies = ['usd', 'eur', 'gbp', 'cad', 'chf', 'aud', 'inr']

    def __init__(self, url=url_v3, currencies=commonCurrencies):
        self.url = url
        self.currencies = currencies
        self.currenciesText = ",".join(currencies)

    def simple_price(self, coin):
        params = {'ids': coin, 'vs_currencies': self.currenciesText}
        response = requests.get(self.url + 'simple/price', params)
        response_json = response.json()
        if coin in response_json:
            return response_json[coin]
        else:
            return []

    def market_chart(self, coin, currency, days):
        params = {'vs_currency': currency, 'days': days}
        response = requests.get(self.url + 'coins/' + coin + '/market_chart',
                                params)
        response_json = response.json()
        if 'prices' in response_json:
            return response_json['prices']
        else:
            return []

    def market_data(self, coin):
        params = {'tickers': False,
                  'community_data': False,
                  'developer_data': False}
        response = requests.get(self.url + 'coins/' + coin, params)
        response_json = response.json()
        if 'market_data' in response_json:
            return response_json['market_data']
        else:
            return []

    def coin_info(self, coin):
        params = {'tickers': False,
                  'community_data': False,
                  'developer_data': False,
                  'market_data': False}
        response = requests.get(self.url + 'coins/' + coin, params)
        response_json = response.json()
        if 'error' in response_json:
            return []
        else:
            return response_json
