import config
import telegram_api
import coingecko_api


def main():
    bot = telegram_api.TelegramRequester(config.bot_token)
    current_offset = None  # Identifier of the first update to be returned
    coinGecko = coingecko_api.CoinGeckoRequester()

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
            if (arguments[0] == '!price' and len(arguments) == 2):

                # Convert spaces in the name of the coin into hyphens
                coin = arguments[1].strip().replace(' ', '-')
                response = coinGecko.simple_price(coin)

                if len(response) > 0:

                    # Equivalence between currencies and emojis
                    emoji_map = {'chf': '🇨🇭', 'inr': '🇮🇳', 'eur': '🇪🇺',
                                 'cad': '🇨🇦', 'aud': '🇦🇺', 'gbp': '🇬🇧',
                                 'usd': '🇺🇸'}
                    # Equivalence between currencies and signs
                    sign_map = {'chf': 'CHF', 'inr': '₹', 'eur': '€',
                                'cad': '$', 'aud': '$', 'gbp': '£',
                                'usd': '$'}
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
