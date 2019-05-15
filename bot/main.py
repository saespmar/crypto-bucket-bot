import datetime
import time
import config
import telegram_api
import coingecko_api
import matplotlib.pyplot as plt
import logging


def main():
    bot = telegram_api.TelegramRequester(config.bot_token)
    current_offset = None  # Identifier of the first update to be returned
    coinGecko = coingecko_api.CoinGeckoRequester()

    # DEBUG: Bot interactions (send, receive messages) and connections
    # INFO: Bot starts/stops and configuration changes
    # WARNING: Connection error
    logLevel = logging.INFO
    logging.basicConfig(
        filename='bot.log',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logLevel
    )
    logging.info('Bot starts')

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

            # If the user edits a previous message, ignore it
            if 'message' not in message:
                chat_id = message['edited_message']['chat']['id']
                logging.debug('Ignored edited message ' +
                              '[Chat: ' + str(chat_id) + ']')
                current_offset = update_id + 1
                continue

            chat_id = message['message']['chat']['id']

            # Check if it's a text message
            if 'text' in message['message']:
                received_text = message['message']['text']
            else:
                logging.debug('Ignored non-text message ' +
                              '[Chat: ' + str(chat_id) + ']')
                current_offset = update_id + 1
                continue

            # arguments[0] -> command
            # arguments[1] -> actual arguments
            arguments = received_text.lower().strip().split(" ", 1)

            # ======================= BASIC COMMANDS ======================= #
            if arguments[0] == '/start':
                output = "Hey " + message['message']['chat']['first_name'] + \
                    "! I'm here to help you manage cryptocurrency " + \
                    "information. Use /help to find out more about how to " + \
                    "interact with me"
                bot.send_message(chat_id, output)
                logging.debug('OK /start ' +
                              '[Chat: ' + str(chat_id) + ']')

            elif arguments[0] == '/help':
                output = "You can control me by sending these commands\n\n" + \
                    "*!price [coin]* - Current price of the " + \
                    "cryptocurrency. " + \
                    "For example: `!price bitcoin`\n\n" + \
                    "*!info [coin]* - Basic information about the " + \
                    "cryptocurrency. " + \
                    "For example: `!info bitcoin`\n\n" + \
                    "*!price_change [interval] [coin]* - Price change " + \
                    "percentage of the cryptocurrency within an interval. " + \
                    "The interval must be 1h, 24h, 7d, 24d, 30d, 60d, " + \
                    "200d or 1y. " + \
                    "For example: `!price_change 7d bitcoin`\n\n" + \
                    "*!evolution [days] [currency] [coin]* - Price " + \
                    "evolution of a coin converted into a currency. " + \
                    "The currency must be chf, inr, eur, cad, aud, gbp " + \
                    "or usd. " + \
                    "For example: `!evolution 15 usd bitcoin`\n\n" + \
                    "*!top_coins [currency]* - Image showing the price " + \
                    "change of the top 10 cryptocurrencies in the last 24 " + \
                    "hours. The currency must be chf, inr, eur, cad, aud, " + \
                    "gbp or usd. " + \
                    "For example: `!top_coins usd`\n\n" + \
                    "*!evolution_img [days] [currency] [coin]* - Image " + \
                    "showing the price evolution of a coin converted into " + \
                    "a currency. The currency must be chf, inr, eur, cad, " + \
                    "aud, gbp or usd. " + \
                    "For example: `!evolution_img 365 usd bitcoin`\n\n" + \
                    "*!market_cap [coin]* - Market capitalization of the " + \
                    "cryptocurrency. " + \
                    "For example: `!market_cap bitcoin`\n\n" + \
                    "*!supply [coin]* - Current supply for the " + \
                    "cryptocurrency. " + \
                    "For example: `!supply bitcoin`"
                bot.send_markdown_message(chat_id, output)
                logging.debug('OK /help ' +
                              '[Chat: ' + str(chat_id) + ']')

            # ======================== SIMPLE PRICE ======================== #
            elif arguments[0] == '!price' and len(arguments) == 2:

                # Convert spaces in the name of the coin into hyphens
                coin = arguments[1].strip().replace(' ', '-')

                try:
                    response = coinGecko.simple_price(coin)
                except:
                    logging.warning('CoinGecko API failed [Simple price]')
                    output = 'The service is unavailable, try again later'
                    bot.send_message(chat_id, output)

                    # Update the offset
                    current_offset = update_id + 1
                    continue

                if len(response) > 0:
                    output = 'The current *' + coin + '* price is:\n'

                    # Build the response
                    for currency in response:
                        output = output + \
                            emoji_map[currency] + ' ' + \
                            formatNumber(response[currency]) + ' ' + \
                            sign_map[currency] + \
                            '\n'
                    logging.debug('OK !price ' +
                                  '[Chat: ' + str(chat_id) + ']')
                else:
                    output = '*' + arguments[1] + '* not found'
                    logging.debug('BAD !price ' +
                                  '[Chat: ' + str(chat_id) + ']')

                bot.send_markdown_message(chat_id, output)

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

                        try:
                            response = coinGecko.market_chart(coin, currency,
                                                              days)
                        except:
                            logging.warning('CoinGecko API failed ' +
                                            '[Market chart]')
                            output = 'The service is unavailable, ' + \
                                'try again later'
                            bot.send_message(chat_id, output)

                            # Update the offset
                            current_offset = update_id + 1
                            continue
                    else:
                        response = []

                    if len(response) > 0:

                        # Return only 12 values
                        cut_point = int(len(response)/11)
                        response = response[0::cut_point]

                        # Build the response
                        output = 'Evolution of *' + \
                                 evolution_args[2].strip() + \
                                 '* in the last ' + days + ' day(s)' +\
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
                                '_' + str(date) + '_\n' + \
                                tendency + ' ' + \
                                formatNumber(price[1]) + ' ' + \
                                sign_map[currency] + '\n\n'

                        bot.send_markdown_message(chat_id, output)
                        logging.debug('OK !evolution ' +
                                      '[Chat: ' + str(chat_id) + ']')
                    else:
                        output = 'Invalid format'
                        bot.send_message(chat_id, output)
                        logging.debug('BAD !evolution ' +
                                      '[Chat: ' + str(chat_id) + ']')
                else:
                    output = 'Invalid format'
                    bot.send_message(chat_id, output)
                    logging.debug('BAD !evolution ' +
                                  '[Chat: ' + str(chat_id) + ']')

            # ================== MARKET CHART WITH IMAGE =================== #
            elif arguments[0] == '!evolution_img' and len(arguments) == 2:

                # evolution_args[0] -> days
                # evolution_args[1] -> currency
                # evolution_args[2] -> coin
                evolution_args = arguments[1].strip().split(" ", 2)

                if len(evolution_args) == 3:
                    days = evolution_args[0]
                    currency = evolution_args[1]
                    coin = evolution_args[2].strip().replace(' ', '-')

                    if currency in sign_map:

                        try:
                            response = coinGecko.market_chart(coin, currency,
                                                              days)
                        except:
                            logging.warning('CoinGecko API failed ' +
                                            '[Market chart]')
                            output = 'The service is unavailable, ' + \
                                'try again later'
                            bot.send_message(chat_id, output)

                            # Update the offset
                            current_offset = update_id + 1
                            continue
                    else:
                        response = []

                    if len(response) > 0:
                        x = []
                        y = []

                        for point in response:

                            # Convert the time deleting milliseconds
                            timestamp = str(point[0])[0: 10]
                            date = datetime.datetime \
                                .fromtimestamp(float(timestamp))

                            # Add values to x-axis and y-axis
                            x.append(date)
                            y.append(point[1])

                        plt.plot(x, y)
                        title = 'Evolution of ' + \
                                evolution_args[2].strip() + \
                                ' in the last ' + days + ' day(s)'
                        plt.title(title)
                        plt.ylabel(currency)  # y-axis showing currency
                        plt.xticks(rotation=90)  # Fit long values in x-axis
                        plt.tight_layout()  # Give enough room to the graph
                        plt.savefig('graph.png')  # Save file to send
                        photo = open('graph.png', 'rb')  # Open file saved
                        bot.send_photo(chat_id, photo)
                        logging.debug('OK !evolution_img ' +
                                      '[Chat: ' + str(chat_id) + ']')
                        photo.close()  # Free resources
                        plt.clf()  # Clear graph
                    else:
                        output = 'Invalid format'
                        bot.send_message(chat_id, output)
                        logging.debug('BAD !evolution_img ' +
                                      '[Chat: ' + str(chat_id) + ']')
                else:
                    output = 'Invalid format'
                    bot.send_message(chat_id, output)
                    logging.debug('BAD !evolution_img ' +
                                  '[Chat: ' + str(chat_id) + ']')

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

                        try:
                            response = coinGecko.market_data(coin)
                        except:
                            logging.warning('CoinGecko API failed ' +
                                            '[Market data]')
                            output = 'The service is unavailable, ' + \
                                'try again later'
                            bot.send_message(chat_id, output)

                            # Update the offset
                            current_offset = update_id + 1
                            continue

                        if len(response) > 0:
                            data = response['price_change_percentage_' +
                                            interval +
                                            '_in_currency']
                            output = 'Price change of *' + coin + \
                                     '* in the last _' + interval + '_:\n'

                            # Build the response
                            for currency in data:
                                if currency in sign_map:
                                    value = formatNumber(data[currency]) + '%'
                                    if data[currency] > 0:
                                        value = '+' + value
                                    output = output + \
                                        emoji_map[currency] + ' ' + \
                                        value + ' ' + \
                                        sign_map[currency] + \
                                        '\n'
                            logging.debug('OK !price_change ' +
                                          '[Chat: ' + str(chat_id) + ']')
                        else:
                            output = '*' + coin + '* not found'
                            logging.debug('BAD !price_change ' +
                                          '[Chat: ' + str(chat_id) + ']')
                    else:
                        output = 'Interval must be ' + \
                                 '`1h`, `24h`, `7d`, `24d`, `30d`, `60d`,' + \
                                 ' `200d` or `1y`'
                        logging.debug('BAD !price_change ' +
                                      '[Chat: ' + str(chat_id) + ']')

                    bot.send_markdown_message(chat_id, output)
                else:
                    output = 'Invalid format'
                    bot.send_message(chat_id, output)
                    logging.debug('BAD !price_change ' +
                                  '[Chat: ' + str(chat_id) + ']')

            # ============= 24H TOP CRYPTOCURRENCIES WITH IMAGE ============ #
            elif arguments[0] == '!top_coins' and len(arguments) == 2:
                currency = arguments[1]

                if currency in sign_map:
                    try:
                        response = coinGecko.coins_markets(currency, 10)
                    except:
                        logging.warning('CoinGecko API failed [Top coins]')
                        output = 'The service is unavailable, try again later'
                        bot.send_message(chat_id, output)

                        # Update the offset
                        current_offset = update_id + 1
                        continue

                    x = []
                    y = []
                    colors = []

                    for crypto in response:
                        x.append(crypto['name'])
                        change = crypto['price_change_percentage_24h']
                        y.append(change)
                        if change < 0:
                            colors.append('r')  # Red color
                        else:
                            colors.append('g')  # Green color

                    plt.bar(x, y, color=colors)
                    plt.title(
                        '24 hours price change of the top 10 cryptocurrencies'
                    )
                    plt.ylabel('% in ' + currency)
                    plt.xticks(rotation=90)  # Fit long names in x-axis
                    plt.tight_layout()  # Give enough room to the graph
                    plt.savefig('graph.png')  # Save file to send
                    photo = open('graph.png', 'rb')  # Open file saved
                    bot.send_photo(chat_id, photo)
                    logging.debug('OK !top_coins ' +
                                  '[Chat: ' + str(chat_id) + ']')
                    photo.close()  # Free resources
                    plt.clf()  # Clear graph
                else:
                    output = "The currency must be chf, inr, eur, cad, " + \
                        "aud, gbp or usd"
                    bot.send_message(chat_id, output)
                    logging.debug('BAD !top_coins ' +
                                  '[Chat: ' + str(chat_id) + ']')

            # ========================= MARKET CAP ========================= #
            elif arguments[0] == '!market_cap' and len(arguments) == 2:

                # Convert spaces in the name of the coin into hyphens
                coin = arguments[1].strip().replace(' ', '-')

                try:
                    response = coinGecko.market_data(coin)
                except:
                    logging.warning('CoinGecko API failed ' +
                                    '[Market data]')
                    output = 'The service is unavailable, try again later'
                    bot.send_message(chat_id, output)

                    # Update the offset
                    current_offset = update_id + 1
                    continue

                if len(response) > 0:
                    data = response['market_cap']
                    output = 'The current *' + coin + '* market cap is:\n'

                    # Build the response
                    for currency in data:
                        if currency in sign_map:
                            output = output + \
                                emoji_map[currency] + ' ' + \
                                formatNumber(data[currency]) + ' ' + \
                                sign_map[currency] + \
                                '\n'
                    logging.debug('OK !market_cap ' +
                                  '[Chat: ' + str(chat_id) + ']')
                else:
                    output = arguments[1] + ' not found'
                    logging.debug('BAD !market_cap ' +
                                  '[Chat: ' + str(chat_id) + ']')

                bot.send_markdown_message(chat_id, output)

            # =========================== SUPPLY =========================== #
            elif arguments[0] == '!supply' and len(arguments) == 2:

                # Convert spaces in the name of the coin into hyphens
                coin = arguments[1].strip().replace(' ', '-')

                try:
                    response = coinGecko.market_data(coin)
                except:
                    logging.warning('CoinGecko API failed ' +
                                    '[Market data]')
                    output = 'The service is unavailable, try again later'
                    bot.send_message(chat_id, output)

                    # Update the offset
                    current_offset = update_id + 1
                    continue

                if len(response) > 0:
                    circulating = response['circulating_supply']
                    output = 'Currently, there are ' + \
                             formatNumber(circulating) + ' *' + coin + '*.'
                    total = response['total_supply']

                    # Additional information if the crypto has finite supply
                    if total is not None:
                        percentage = (circulating/total)*100
                        output = output + ' The supply stops at ' + \
                            formatNumber(total) + ' *' + coin + '*.'
                        output = output + ' That means ' + \
                            formatNumber(percentage) + '% of *' + coin + \
                            '* has been issued.'
                    logging.debug('OK !supply ' +
                                  '[Chat: ' + str(chat_id) + ']')
                else:
                    output = '*' + arguments[1] + '* not found'
                    logging.debug('BAD !supply ' +
                                  '[Chat: ' + str(chat_id) + ']')

                bot.send_markdown_message(chat_id, output)

            # ========================= INFORMATION ======================== #
            elif arguments[0] == '!info' and len(arguments) == 2:

                # Convert spaces in the name of the coin into hyphens
                coin = arguments[1].strip().replace(' ', '-')

                try:
                    response = coinGecko.coin_info(coin)
                except:
                    logging.warning('CoinGecko API failed [Coin info]')
                    output = 'The service is unavailable, try again later'
                    bot.send_message(chat_id, output)

                    # Update the offset
                    current_offset = update_id + 1
                    continue

                if len(response) > 0:
                    output = '*' + response['name'] + \
                        ' (' + response['symbol'] + ')*\n\n'

                    links = response['links']
                    twitter_url = links['twitter_screen_name']
                    if len(twitter_url) > 0:
                        twitter_url = 'https://twitter.com/' + twitter_url

                    facebook_url = links['facebook_username']
                    if len(facebook_url) > 0:
                        facebook_url = 'https://www.facebook.com/' + \
                            facebook_url

                    telegram_channel = links['telegram_channel_identifier']
                    if len(telegram_channel) > 0:
                        telegram_channel = '@' + telegram_channel

                    output = output + \
                        'Webpage: ' + links['homepage'][0] + '\n' + \
                        'Twitter: ' + twitter_url + '\n' + \
                        'Facebook: ' + facebook_url + '\n' + \
                        'Telegram: ' + telegram_channel + '\n' + \
                        'Subreddit: ' + links['subreddit_url'] + '\n\n'

                    if response['genesis_date'] is not None:
                        inverted_date = response['genesis_date']
                        correct_date = datetime.datetime \
                            .strptime(inverted_date, '%Y-%m-%d') \
                            .strftime('%d/%m/%Y')
                        output = output + \
                            '- Genesis date: ' + correct_date + '\n'

                    output = output + \
                        '- CoinGecko rank: ' + \
                        str(response['coingecko_rank']) + '\n'

                    output = output + \
                        '- Block time: ' + \
                        str(response['block_time_in_minutes']) + ' minutes\n'

                    logging.debug('OK !info ' +
                                  '[Chat: ' + str(chat_id) + ']')
                else:
                    output = '*' + arguments[1] + '* not found'
                    logging.debug('BAD !info ' +
                                  '[Chat: ' + str(chat_id) + ']')

                bot.send_markdown_message(chat_id, output)

            else:
                logging.debug('Unknown command ' +
                              '[Chat: ' + str(chat_id) + ']')
                output = 'Invalid format'
                bot.send_message(chat_id, output)

            # Update the offset
            current_offset = update_id + 1


def formatNumber(number):

    # Add thousands separator
    commaSeparator = "{:,}".format(number)

    # Replace commas with dots and vice versa
    num = commaSeparator.replace('.', '|').replace(',', '.').replace('|', ',')

    # Check it has at least 2 decimal places
    divide = num.split(',')
    if len(divide) == 1:
        num = num + ',00'  # No decimals, add 2
    if len(divide) == 2 and len(divide[1]) == 1:
        num = num + '0'  # Only 1 decimal, add 1

    return num


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.info('Bot manually disconnected')
        exit()
