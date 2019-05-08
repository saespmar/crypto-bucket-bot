<p align="center">
  <img src="https://raw.githubusercontent.com/saespmar/crypto-bucket-bot/master/images/Logo.png" alt="logo" width="200">
</p>
<p align="center">
  <img src="https://img.shields.io/badge/status-unfinished-red.svg" alt="status">
</p>

# Crypto Bucket Bot
**Crypto Bucket Bot** is a Telegram bot that helps users to check the status of the most important cryptocurrencies through the [CoinGecko API](https://www.coingecko.com/en/api).

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Prerequisites

First of all, you need a Telegram account. You can create one downloading their app on your phone and linking a phone number to it.

Once your account is ready, start a chat with [@BotFather](https://t.me/botfather) and follow the instructions until you get a token to access the HTTP API. This token should be placed in `bot/config.py` and should be stored in a *bot_token* variable. [Here](bot/config.py.example) is an example.

Also, Python 3 with the pip package manager needs to be installed on your computer. Then, run this command in order to get the *requests* package:

```
pip install requests
```

### Running

Execute the `bot/main.py` file and start chatting with the bot!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
