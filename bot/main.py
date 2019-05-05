import datetime
import time
import config
import telegram_api
import coingecko_api


def main():
    bot = telegram_api.TelegramRequester(config.bot_token)
    current_offset = None  # Identifier of the first update to be returned
    coinGecko = coingecko_api.CoinGeckoRequester()

    # Equivalence between currencies and emojis
    emoji_map = {'chf': '🇨🇭', 'inr': '🇮🇳', 'eur': '🇪🇺', 'cad': '🇨🇦',
                 'aud': '🇦🇺', 'gbp': '🇬🇧', 'usd': '🇺🇸'}
    # Equivalence between currencies and signs
    sign_map = {'chf': 'CHF', 'inr': '₹', 'eur': '€', 'cad': '$',
                'aud': '$', 'gbp': '£', 'usd': '$'}

    # Infinite loop doing long polling (30 seconds by default)
    while True:
        unread_messages = bot.get_updates(current_offset)

        for message in unread_messages:
            update_id = message['update_id']
            chat_id = message['message']['chat']['id']

            # Check if it's a text message
            if 'text' in message['message']:
                received_text = message['message']['text']
            else:
                received_text = ''

            # arguments[0] -> command
            # arguments[1] -> actual arguments
            arguments = received_text.lower().strip().split(" ", 1)

            # ======================== SIMPLE PRICE ======================== #
            if arguments[0] == '!price' and len(arguments) == 2:

                # Convert spaces in the name of the coin into hyphens
                coin = arguments[1].strip().replace(' ', '-')
                response = coinGecko.simple_price(coin)

                if len(response) > 0:
                    output = ''

                    # Build the response
                    for currency in response:
                        output = output + \
                            emoji_map[currency] + ' ' + \
                            str(response[currency]) + ' ' + \
                            sign_map[currency] + \
                            '\n'

                else:
                    output = arguments[1] + ' not found'

            # ======================== MARKET CHART ======================== #
            elif arguments[0] == '!evolution' and len(arguments) == 2:

                # evolution_args[0] -> days
                # evolution_args[1] -> currency
                # evolution_args[2] -> coin
                evolution_args = arguments[1].strip().split(" ", 2)

                if len(evolution_args) == 3:
                    days = evolution_args[0]
                    currency = evolution_args[1]
                    coin = evolution_args[2].strip().replace(' ', '-')

                    if currency in sign_map:
                        response = coinGecko.market_chart(coin, currency, days)
                    else:
                        response = []

                    if len(response) > 0:

                        # Return only 12 values
                        cut_point = int(len(response)/11)
                        response = response[0::cut_point]

                        # Build the response
                        output = 'Evolution of ' + evolution_args[2].strip() +\
                                 ' in the last ' + days + ' day(s)' +\
                                 ' ' + emoji_map[currency] + '\n\n'
                        for index, price in enumerate(response):

                            # Convert the time deleting milliseconds
                            timestamp = str(price[0])[0: 10]
                            date = datetime.datetime \
                                .fromtimestamp(float(timestamp)) \
                                .strftime('%d/%m/%Y -- %H:%M')

                            # Check if the price has increased or not
                            if index > 0:
                                if response[index-1][1] > response[index][1]:
                                    tendency = '⬇️'
                                elif response[index-1][1] < response[index][1]:
                                    tendency = '⬆️'
                                else:
                                    tendency = '➡️'
                            else:
                                tendency = '⏹️'

                            # Get all together
                            output = output + \
                                str(date) + '\n' + \
                                tendency + ' ' + \
                                str(price[1]) + ' ' + \
                                sign_map[currency] + '\n\n'

                    else:
                        output = 'Invalid format'
                else:
                    output = 'Invalid format'

            else:
                output = 'Invalid format'

            # Reply
            bot.send_message(chat_id, output)

            # Update the offset
            current_offset = update_id + 1


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
