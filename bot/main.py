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
                    output = 'The current ' + coin + ' price is:\n'

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

            # ======================== PRICE CHANGE ======================== #
            elif arguments[0] == '!price_change' and len(arguments) == 2:

                # price_change[0] -> interval
                # price_change[1] -> coin
                price_change = arguments[1].strip().split(" ", 1)

                if len(price_change) == 2:
                    interval = price_change[0]
                    allowed_interval = {'1h', '24h', '7d', '14d',
                                        '30d', '60d', '200d', '1y'}
                    coin = price_change[1].strip().replace(' ', '-')
                    if interval in allowed_interval:
                        response = coinGecko.market_data(coin)
                        if len(response) > 0:
                            data = response['price_change_percentage_' +
                                            interval +
                                            '_in_currency']
                            output = 'Price change of ' + coin + \
                                     ' in the last ' + interval + ':\n'

                            # Build the response
                            for currency in data:
                                if currency in sign_map:
                                    value = str(data[currency]) + '%'
                                    if data[currency] > 0:
                                        value = '+' + value
                                    output = output + \
                                        emoji_map[currency] + ' ' + \
                                        value + ' ' + \
                                        sign_map[currency] + \
                                        '\n'
                        else:
                            output = coin + ' not found'
                    else:
                        output = 'Interval must be ' + \
                                  '1h, 24h, 7d, 24d, 30d, 60d, 200d or 1y'
                else:
                    output = 'Invalid format'

            # ========================= MARKET CAP ========================= #
            if arguments[0] == '!market_cap' and len(arguments) == 2:

                # Convert spaces in the name of the coin into hyphens
                coin = arguments[1].strip().replace(' ', '-')
                response = coinGecko.market_data(coin)

                if len(response) > 0:
                    data = response['market_cap']
                    output = 'The current ' + coin + ' market cap is:\n'

                    # Build the response
                    for currency in data:
                        if currency in sign_map:
                            value = "{:,}".format(data[currency])
                            output = output + \
                                emoji_map[currency] + ' ' + \
                                value + ' ' + \
                                sign_map[currency] + \
                                '\n'

                else:
                    output = arguments[1] + ' not found'

            # =========================== SUPPLY =========================== #
            if arguments[0] == '!supply' and len(arguments) == 2:

                # Convert spaces in the name of the coin into hyphens
                coin = arguments[1].strip().replace(' ', '-')
                response = coinGecko.market_data(coin)

                if len(response) > 0:
                    circulating = response['circulating_supply']
                    output = 'Currently, there are ' + \
                             str(circulating) + ' ' + coin + '.'
                    total = response['total_supply']

                    # Additional information if the crypto has finite supply
                    if total is not None:
                        percentage = (circulating/total)*100
                        output = output + ' The supply stops at ' + \
                            str(total) + ' ' + coin + '.'
                        output = output + ' That means ' + str(percentage) + \
                            '% of ' + coin + ' has been issued.'

                else:
                    output = arguments[1] + ' not found'

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
