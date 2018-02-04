# bot.py

import random
from io import BytesIO
import requests
import tweepy
from PIL import Image
from PIL import ImageFile
from secrets import *
import logging


ImageFile.LOAD_TRUNCATED_IMAGES = True

#create an OAuthHandler instance
# Twitter requires all requests to use OAuth for authentication
auth = tweepy.OAuthHandler(consumer_key, consumer_secret) 

auth.set_access_token(access_token, access_secret)

 #Construct the API instance
api = tweepy.API(auth) # create an API object

def tweet_image(url, username, status_id):
    filename = 'temp.png'
    # send a get request
    request = requests.get(url, stream=True)
    if request.status_code == 200:
        # read data from downloaded bytes and returns a PIL.Image.Image object
        i = Image.open(BytesIO(request.content))
        # Saves the image under the given filename
        i.save(filename)
        scramble(filename)
        # Update the authenticated user’s status
        api.update_with_media('scramble.png', status='@{0}'.format(username), in_reply_to_status_id=status_id)
    else:
        print("unable to download image")

def scramble(filename):
    BLOCKLEN = 64  # Adjust and be careful here.

    img = Image.open(filename)
    width, height = img.size

    xblock = width // BLOCKLEN
    yblock = height // BLOCKLEN
    # creates sequence of 4-tuples (box) defining the left, upper, right, and lower pixel coordinate
    blockmap = [(xb * BLOCKLEN, yb * BLOCKLEN, (xb + 1) * BLOCKLEN, (yb + 1) * BLOCKLEN)
                for xb in range(xblock) for yb in range(yblock)]

    shuffle = list(blockmap)

    # shuffle the sequence
    random.shuffle(shuffle)

    # Creates a new image with the given mode and size.
    result = Image.new(img.mode, (width, height))
    for box, sbox in zip(blockmap, shuffle):
        # Returns a rectangular region from this original image.
        crop = img.crop(sbox)
        # Pastes the cropped pixel into the new image Object
        result.paste(crop, box)
    result.save('scramble.png')

def tidePodOrNah(url, username, status_id):
    # send a get request
    request = requests.get(url, stream=True)
    if (request.status_code == 200):

        '''
        # read data from downloaded bytes and returns a PIL.Image.Image object
        i = Image.open(BytesIO(request.content))
        # Saves the image under the given filename
        i.save(filename)
        #classify image
        '''
        return True

def generateResponse():
    return

def printTweets(api):
    public_tweets = api.home_timeline()
    for tweet in public_tweets:
        print(tweet.text)

def getFollowers(api, username):
    user = api.get_user(username)
    for friend in user.friends():
        print(friend.screen_name)

def respond(tide, tweet, username, hashtags):
    if 'shutdown' in tweet:
        raise Exception
    reply = '' 
    tideFound = False

    for t in tide:
        if(t[1]):
            tideFound = True
            reply += '1'
        else:
            reply += '0'

        reply += ','

    if(tideFound): #TidePod

        reply = DoThIsToTwEeT(tweet, username)
    else: #NotTidePod
        reply = scrambleTweet(tweet)
        #reply = DoThIsToTwEeT(tweet, username)
    return reply

def DoThIsToTwEeT(tweet, username):
    words = tweet.split(' ')
    respond = []
    reply = ' '
    for word in words:
        if(word == username or words[1:]==username):
            respond.append(word)
            continue
        temp = ''
        for i,c in enumerate(word):
            if(i%2==0):
                temp += c.upper()
            else:
                temp += c.lower()
        respond.append(temp)
    return reply.join(respond)

def scrambleTweet(tweet):
    words = tweet.split(' ')
    randomWords = []
    reply = ' '
    while(len(words) > 0):
        word = words.pop( random.randrange(len(words)) )
        randomWords.append(word)
    return reply.join(randomWords)

#create a class in
#herithing from the tweepy  StreamListener
class BotStreamer(tweepy.StreamListener):

    # Called when a new status arrives which is passed down from the on_data method of the StreamListener
    def on_status(self, status):
        print('here')
        username = status.user.screen_name 
        status_id = status.id
        print(status_id)

        if(username == 'tidepodbot'):
            print('tweeting at self')
            return

        tweet = status.text
        hashtags = []
        if 'hashtags' in status.entities:
            for hashtag in status.entities['hashtags']:
                hashtags.apped(hashtag['text'])

        # ntities provide strured data from Tweets including resolved URLs, media, hashtags 
        # and mentions without having to parse the text to extract that information
        tidePods = []
        if 'media' in status.entities:
            for index, image in enumerate(status.entities['media']):
                #tweet_image(image['media_url'], username, status_id)
                tide = tidePodOrNah(image['media_url'])
                tidePods.append((index, tide)) #tuple index and if tidePod

        reply = respond(tidePods, tweet, username, hashtags)

        #tweet = ("@{} this may or may not be a tide pod...".format(username))
        api.update_status( ('@{} ' + reply).format(username), in_reply_to_status_id=status_id)

myStreamListener = BotStreamer()

#Construct the Stream instance

stream = tweepy.Stream(auth, myStreamListener)
print('start')
try:
    stream.filter(track=['@tidepodbot'])
except Exception as e:
    logging.exception("Something awful happened!")
    print('something is broken')
stream.disconnect()
print('stop')
