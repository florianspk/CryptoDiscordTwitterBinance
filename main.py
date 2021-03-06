from binance_api import BinanceApi
from textblob import TextBlob
# import discord
import configparser
import tweepy
import mysql.connector
from mysql.connector import errorcode
from datetime import datetime

# client = discord.Client()
# Read 'conf.ini' file to get twitter API credentials and other constants
parser = configparser.ConfigParser()
parser.read('conf.ini')

TWITTER_API_KEY = parser.get('twitter_credentials', 'api_key')
TWITTER_API_KEY_SECRET = parser.get('twitter_credentials', 'api_key_secret')
ACCESS_TOKEN = parser.get('twitter_credentials', 'access_token')
ACCESS_TOKEN_SECRET = parser.get('twitter_credentials', 'access_token_secret')

BINANCE_API_KEY = parser.get('binance_credentials', 'api_key')
BINANCE_API_KEY_SECRET = parser.get('binance_credentials', 'api_key_secret')

FOLLOWED_USERS = [id for _, id in parser.items('followed_users')]

TRACKED_COINS = {
    text_in_tweet: binance_pair for binance_pair, text_in_tweet in parser.items('coins')
    for text_in_tweet in text_in_tweet.split(', ')
}

NEGATIVES_WORDS = {
    word: polarity for word, polarity in parser.items('negative_words')
}
# Discord Notification
# NOTIFICATION_TOKEN = parser.get('Discord', 'bot_token')
# client.run(NOTIFICATION_TOKEN)


# OAuth with Twitter API
auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_KEY_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
twitter_api = tweepy.API(auth)

# OAuth with Binance API
binance_api = BinanceApi(BINANCE_API_KEY, BINANCE_API_KEY_SECRET)

# BDD

DB_HOST = parser.get('Database', 'host')
DB_USER = parser.get('Database', 'user')
DB_PASSWORD = parser.get('Database', 'password')
DB_PORT = parser.get('Database', 'port')
DB_DATABASE = parser.get('Database', 'database')


# @client.event
# async def on_ready():
#     print("Le bot est prêt !")


# Streaming for listening to tweets
def check_sentence_for_coins(sentence: str) -> str:
    """Returns the corresponding binance pair if a string contains any words refering to a followed coins
    Args:
        sentence (str): the sentence
    Returns:
        str: the binance pair if it contains a coins, otherwise returns 'NO_PAIR'
    """
    coin = next((word for word in list(TRACKED_COINS.keys()) if word in sentence.lower()), 'NO_PAIR')

    if coin != 'NO_PAIR':
        return TRACKED_COINS[coin]

    return coin


def is_positive_sentence(sentence: str) -> bool:
    """Returns true if the sentence is mainly positive
    Args:
        sentence (str): the sentence
    Returns:
        bool: true if the sentence is mainly positive
    """
    analysis = TextBlob(sentence)
    custom_polarity = 0

    for word in sentence.split(' '):
        if word.lower() in NEGATIVES_WORDS:
            custom_polarity += int(NEGATIVES_WORDS[word])

    return analysis.sentiment.polarity - custom_polarity >= 0


def trade_coin(binance_pair: str, percentage_usdt_balance: float) -> None:
    """Try to initialize a trade
    Args:
        binance_pair (str): binance pair to trade
        percentage_usdt_balance (float): percentage of total usdt balance on the account to put on the trade
    """
    highest_buy_order = binance_api.get_highest_buy_order(binance_pair)

    if binance_api.is_close_to_average_price(binance_pair, highest_buy_order):
        usdt_balance = binance_api.get_usdt_balance()

        quantity = round((usdt_balance / highest_buy_order) * percentage_usdt_balance,
                         8)  # rounds up to 8 digits, see binance api max precision

        binance_api.place_buy_order(binance_pair, quantity, highest_buy_order,
                                    sell_price=highest_buy_order * 1.15)  # 15% benefits

    else:
        print(f'Too much volatility on the pair ${binance_pair}')


class TweetStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        # Skip tweets that are not posted by any of the followed users (replies, retweets from other users ..)
        if status.user.id_str not in FOLLOWED_USERS:
            return
        print(f'New message form : {status.user.id_str} - {status.text}')

        binance_pair = check_sentence_for_coins(status.text)

        if binance_pair != 'NO_PAIR':
            # Sentiment analysis => only buy if the sentence is positive
            try:
                cnx = mysql.connector.connect(user=DB_USER, password=DB_PASSWORD,
                                              host=DB_HOST, port=DB_PORT,
                                              database=DB_DATABASE)
                mycursor = cnx.cursor()
                sql = "INSERT INTO Scape_twitter.twitter_analyze (user_id, content, crypto, date_post, bot_good_sentence ) VALUES (%s, %s, %s, %s, %s);"
                now = datetime.now()
                createAt = now.strftime('%Y-%m-%d %H:%M:%S')
                val = (status.user.id_str, status.text, binance_pair, createAt, is_positive_sentence(status.text))
                mycursor.execute(sql, val)
                cnx.commit()
                print(mycursor.rowcount, "was inserted")
                if is_positive_sentence(status.text):
                    print("TODO Traide")
                    # TODO FAIRE UNE DEMANDE AVANT DE TRADE
                    # trade_coin(binance_pair.upper(), 0.1)  # 10% in
                else:
                    print(f'negative sentence : {status.text}')
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    print("Something is wrong with your user name or password")
                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                    print("Database does not exist")
                else:
                    print(err)
        else:
            print("NO_PAIR_FIND")


# Start the stream
tweetStreamListener = TweetStreamListener()
tweetStream = tweepy.Stream(auth=twitter_api.auth, listener=tweetStreamListener)

tweetStream.filter(follow=FOLLOWED_USERS, is_async=True)
