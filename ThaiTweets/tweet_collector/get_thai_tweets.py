#this will connect us to tweets in real-time
import tweepy
import pymongo
try:
    import cPickle as pickle
except ImportError: 
    import pickle
import re

with open('Emoji_Dict.p', 'rb') as fp:
    Emoji_Dict = pickle.load(fp)
Emoji_Dict = {v: k for k, v in Emoji_Dict.items()}


client = pymongo.MongoClient(host='mongodb', port=27017)
db = client.twitter_go
tweets = db.tweets


API_KEY = "JLKxDeW9k6sxh5vmUDypuZN2j"
API_SECRET = "ANXEZmFqYjYWjxlvt76jZNI4mMlySQw5XI8MmiUsHie1UKMNbX"
ACCESS_TOKEN = "36755340-ERBmQae6NZUt4Y6UCQSQrylR2IRobPo1fuQh12EVY"
ACCESS_TOKEN_SECRET = "JOMb5l1WrApS7AEMNYWKNl2FUoEDZtZ2B2IYDyeLFlbvg"


def convert_emojis_to_word(text):
    for emot in Emoji_Dict:
        text = re.sub(r'('+emot+')', "_".join(Emoji_Dict[emot].replace(",","").replace(":","").split()), text)
    return text

def get_auth_handler():
    """
    Function for handling Twitter Authentication. See course material for 
    instructions on getting your own Twitter credentials.
    """
    auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    return auth


class MaxTweetsListener(tweepy.StreamListener):

    def __init__(self, max_tweets, *args, **kwargs):
        # initialize the StreamListener
        super().__init__(*args, **kwargs)
        # set the instance attributes
        self.max_tweets = max_tweets
        self.counter = 0

    def on_connect(self):
        print('Connected. Listening for incoming tweets')

    def on_status(self, status):
        """Whatever we put in this method defines what is done with
        every single tweet as it is intercepted in real-time"""

        # increase the counter
        self.counter += 1

        tweet = {
            'text': convert_emojis_to_word(status.text).encode('utf-8'),
            'username': status.user.screen_name,
            'followers_count': status.user.followers_count
        }
        result = convert_emojis_to_word(f'\n{tweet["text"]}\n')
    
        print(f'New tweet arrived: {result}\n', flush=True)
        with open('results.txt', 'a')as f:
            f.write(result)
            
        #print(type({tweet['text']}))
        tweets.insert_one({'text': result})

        # check if we have enough tweets collected
        if self.max_tweets == self.counter:
            # reset the counter
            self.counter = 0
            # return False to stop the listener
            return False

    def on_error(self, status):
        if status == 420:
            print(f'Rate limit applies. Stop the stream.')
            return False


if __name__ == '__main__':
    auth = get_auth_handler()
    listener = MaxTweetsListener(max_tweets=10_000)
    stream = tweepy.Stream(auth, listener)
    stream.filter(track=['Thailand'], languages=['en'], is_async=False)