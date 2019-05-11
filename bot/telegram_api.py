import requests


class TelegramRequester:

    def __init__(self, token):
        self.token = token
        self.url = "https://api.telegram.org/bot{}/".format(token)

    def get_updates(self, offset=None, timeout=30):
        params = {'offset': offset, 'timeout': timeout}
        response = requests.get(self.url + 'getUpdates', params)
        return response.json()['result']

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        return requests.post(self.url + 'sendMessage', params)

    def send_markdown_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
        return requests.post(self.url + 'sendMessage', params)
