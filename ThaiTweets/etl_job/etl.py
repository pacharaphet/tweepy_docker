import logging 
import psycopg2
from sqlalchemy import create_engine
import pymongo
import time 
import re 
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

time.sleep(10)
#connect to mongodb server 
client = pymongo.MongoClient(host='mongodb', port=27017)
#select database to use in mongodb
db = client.twitter_go
s = SentimentIntensityAnalyzer()
#connect to postgres
pg = create_engine('postgresql://pacharaphet:001212@postgresdb:5432/thai_tweets', echo=True)
#create table for insertion
now = datetime.now()
pg.execute('''
    CREATE TABLE IF NOT EXISTS tweets ( 
    text VARCHAR(1000),
    sentiment NUMERIC);''')


docs = db.tweets.find()

def loop_docs():
    '''Send tweets to the db and make a list...will choose one'''
    
    keep_going = True
    while keep_going == True: 

        for doc in docs:

            logging.critical('this is a doc!!!!!!')
            text = doc['text']
            text = ' '.join(re.findall('(?u)\\b\\w\\w+\\b',text.lower()))
            text = re.sub(r' ?xe2 x80 x99', "'", text)
            text = re.sub(r'\xe2\x80\xa6', "...", text)
            text = re.sub(r'https.* ', '', text)
            text = re.sub(r'\xf0\x9f\xa5\xba\n', '<sad_face>', text)
            text = re.sub(r'\xf0\x9f\x87\xb9\xf0\x9f\x87\xad\n', 'TH', text)
            logging.critical(text)
            sentiment = s.polarity_scores(text)
            score = sentiment['compound']
            query = "INSERT INTO tweets VALUES (%s, %s);"
            dt = now.strftime("%d/%m/%Y %H:%M:%S")
            pg.execute(query, (text, score))
            time.sleep(5)
            #need something to tell it to wait longer if it doesn't find anything I think, tho maybe not
    return True 

loop_docs()