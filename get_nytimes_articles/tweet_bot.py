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

def compose_tweet():
    """Create the text of the tweet to be sent"""
     
    
    compose = ""
    char_lim = 140
    num_verse = random.randrange(len(lyrics))
    selected_verse = lyrics[num_verse]
   
    line_count = 0
    while (line_count < len(selected_verse)) and \
	len(compose)+len(selected_verse[line_count]) < char_lim:
        if line_count != 0:
            compose += " / "
        compose += selected_verse[line_count]
 
        line_count += 1
    return compose  

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

    # Send the tweet and log success or failure
    try:
        api.update_status(text)
    except tweepy.error.TweepError as e:
        log(e.message)
    else:
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

        month_urls = get_articles()
        used_urls = get_used_urls(used_urls_csv)
        found_haiku = check_haiku(month_urls, used_urls)
        if found_haiku:
            tweet_text = compose_tweet()
            tweet(tweet_text)
        else:
            log("No haiku's found in remaining urls for month")

        time.sleep(7200)

if __name__ == "__main__":
    main() 
