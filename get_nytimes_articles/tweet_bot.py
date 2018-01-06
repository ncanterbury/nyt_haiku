import time
import random
import os 
import tweepy
from secrets import *
from time import gmtime, strftime
from getTimesArticles import *

# ====== Individual bot configuration ==========================
bot_username = 'nyt_haiku'
logfile_name = bot_username + ".log"
# ==============================================================

def compose_tweet(headline_and_haiku):
    """Create the text of the tweet to be sent"""
     
    compose = ""
    char_lim = 140
    line_count = 0
    character_count = 0
    syl_count = 0
    print 'THIS IS IT'
    print headline_and_haiku

    headline = headline_and_haiku[0]
    haiku = headline_and_haiku[1]

    for word in haiku:
        if line_count == 0:
            syl_count += word[1] 
            if syl_count == 5:
                compose += word[0]+"\n"
                line_count = 1
                continue
            else:
                compose += word[0]+" "
        if line_count == 1:
            syl_count += word[1]
            if syl_count == 12:
                compose += word[0]+"\n"
                line_count = 2
                continue
            else:
                compose += word[0]+" "
        if line_count == 2:
            syl_count += word[1]
            if syl_count == 17:
                compose += word[0]
            else:
                compose += word[0]+" "

    print 'gotten'
    # add headline 
    compose += "\n\n" + headline 
    print compose 
    return compose  

def process_haiku(text):
    split_haiku = text.split(" ")
    return split_haiku

def get_config():
    config = SafeConfigParser()
    script_dir = os.path.dirname(__file__)
    config_file = os.path.join(script_dir, 'settings.cfg')
    config.read(config_file)

    used_urls_csv = config.get('files','used_urls')
    log_file = config.get('files','logfile')

    api_key = config.get('nytimes','api_key')
    year = config.get('nytimes','year')
    month = config.get('nytimes','month')
    used_urls_csv = config.get('files', 'used_urls')
    
    ret = [api_key, year, month, used_urls_csv]
    return ret 

def tweet(text):
    """Send out the text as a tweet."""
    # Twitter authentication 
    auth = tweepy.OAuthHandler(C_KEY, C_SECRET)
    auth.set_access_token(A_TOKEN, A_TOKEN_SECRET)
    api = tweepy.API(auth)
    print 'wthat the fuck'

    # Send the tweet and log success or failure
    try:
        api.update_status(text)
        print 'did work'
    except tweepy.error.TweepError as e:
        print 'nope'
        print e
        log(e.message)
    else:
        print 'tweeted'
        log("Tweeted " + text)
    
def log(message):
    """Log message to logfile"""
    path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
   # with open(os.path.join(path, logfile_name), 'a+') as f:
    #    t = strftime("%d %b %Y %H:%M:%S", gmtime())
    #    f.write("\n" + t + " " + message)


def main():
    while True:
        config_info = get_config()
        api_key = config_info[0]
        year = config_info[1]
        month = config_info[2]
        used_urls_csv = config_info[3]
        #month_urls = ['https://www.nytimes.com/2018/01/02/science/donkeys-africa-china-ejiao.html','https://www.nytimes.com/2018/01/01/us/politics/trump-businesses-regulation-economic-growth.html', 'https://www.nytimes.com/2018/01/01/insider/lebanon-palestine-scoop-saad-hariri.html', 'https://www.nytimes.com/2018/01/01/opinion/online-shopping-sales-tax.html', 'https://www.nytimes.com/2018/01/01/opinion/was-america-duped-at-khe-sanh.html']
        month_urls = get_articles(api_key, year, month)
        list_used_urls = get_used_urls(used_urls_csv)
        found_haiku = check_haiku(month_urls, list_used_urls, used_urls_csv)
        if found_haiku:
            tweet_text = compose_tweet(found_haiku)
            print 'gonna tweet'
            tweet(tweet_text)
        else:
            log("No haiku's found in remaining urls for month")

        time.sleep(7200)

if __name__ == "__main__":
    main() 
