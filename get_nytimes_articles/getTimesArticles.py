import urllib2
import curses
from curses.ascii import isdigit
import nltk
from nltk.corpus import cmudict
import re
import csv
import codecs
import sys, os
from ConfigParser import SafeConfigParser
import logging 
from pprint import pprint 
import json
from lxml import html 
import requests

added_words = {'simpletons': 3, 'disembarked': 3, 'drippy': 2}
def get_used_urls(used_url_csv):
    used_urls = []

    with open(used_url_csv, 'r') as urls_csv:
        readCSV = csv.reader(urls_csv, delimiter=',')
        for row in readCSV:
            print row
            used_urls.append(row[0])

    print used_urls
    print ('https://www.nytimes.com/2018/01/02/science/donkeys-africa-china-ejiao.html' in used_urls)
    return used_urls


def convert(input):
    if isinstance(input, dict):
        return {convert(key): convert(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [convert(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

def get_articles(api_key, year, month):
    year = str(year)
    month = str(month)
    api_key = str(api_key)

    # get all articles for the month
    request_string = "https://api.nytimes.com/svc/archive/v1/" + year + "/" + month + ".json?" + "&api-key=" + api_key
    response = urllib2.urlopen(request_string)
    content = response.read()

    # build list "urls" containing urls of all articles for the month
    urls = []
    if content:
        articles = convert(json.loads(content))
        # if there are articles here
        num_articles = len(articles['response']['docs'])
        print num_articles
        
        for index in range(num_articles):
            urls.append(articles['response']['docs'][index]['web_url'])
        print urls
        

        print articles["response"]["docs"][0]["web_url"]

    return urls

def has_numbers(string):
    return any(char.isdigit() for char in string)

def get_text(url):
    page = requests.get(url)
    tree = html.fromstring(page.content)
    article = tree.xpath('//*[contains(@class,"story-body-text")]/text()')
    if article == []:
        article = tree.xpath('//*[contains(@class,"Paragraph-paragraph--2eXNE")]/text()')
    
    print 'Article', article 
    print ""
    print ""
    ret = []
    for sentence in article:
        sentence = re.sub(r'\xe2\x80\x99', "'", sentence)
        sentence = re.sub(r'\xe2\x80\x9c', '"', sentence)
        sentence = re.sub(r'\xe2\x80\x9d', '"', sentence)
        sentence = re.sub(r'\xe2\x80\x94', "--", sentence)
        sentence = re.sub(r'\xa0', "", sentence)
        sentence_list = re.split(r'(?<=[.])(?<!\d.)\s', sentence)
        for sentence in sentence_list:
            if sentence == "":
                continue
            if sentence[-1] == '"' and sentence[0] != '"':
                sentence = sentence[:-1]
            if sentence[0] != " " and (sentence[-1] == "." or sentence[-1] == '"') \
                    and sentence[0] != "." and sentence[0] != ",":
                if not has_numbers(sentence):
                    sentence.encode('utf-8')
                    ret.append(sentence)
                    print sentence

    print "this is ret"
    return ret

def is_haiku(text):
    print "Beginning is haiku"
    print ""

    # this is here because we cant deal with foreign character yet
    # maybe will be fixed 

    text_orig = text
    '''
    try:
        text_orig = str(text)  
    except:
        return False
    '''
    text = text.lower()
    print text
    text = re.sub(r"'ve", "", text)
    text = re.sub(r"n't", " not", text)
    print text
    words = nltk.wordpunct_tokenize(re.sub('[^a-zA-Z_ ]', '',text))

    syl_count = 0
    word_count = 0
    haiku_line_count = 0
    lines = []
    d = cmudict.dict()

    for word in words:
        print ""
        print word
        word_syl_count = 0

        flag = -1
        if word.lower() in d:
            check = d[word.lower()]
        elif word.lower() in added_words:
            check = added_words[word.lower()]
            flag = 1
        else:
            return False 

        if flag == -1:
            for pos in check[0]:
                if has_numbers(pos):
                    word_syl_count += 1
        else:
            word_syl_count += check

        syl_count += word_syl_count
        print syl_count 
        word_count += 1

        if haiku_line_count == 0:
            if syl_count == 5:
                haiku_line_count += 1
            elif syl_count > 5:
                return False 
        elif haiku_line_count == 1:
            if syl_count == 12:
                haiku_line_count += 1
            elif syl_count > 12:
                return False 
        else:
            if syl_count == 17:
                print 'running here'
                print word
                print text_orig[-1]
                print text_orig.split(" ")[-1]
                print (word+"." == text_orig[-1])
                if word+"." != text_orig.split(" ")[-1] \
                        and word+'."' != text_orig.split(" ")[-1]: 
                    return False 
                else:
                    return text_orig
            elif syl_count > 17:
                return False 

    print words 

def check_haiku(month_urls, used_urls):
    '''
    Get text from unused/unchecked article, call is_haiku to see if haiku
    in text. text processing done by get_text
    '''
    
    count = 0
    for url in month_urls:
        if count == 5:
            break
        if url not in used_urls:
            article_text = get_text('https://www.nytimes.com/2017/06/02/style/modern-love-making-a-marriage-magically-tidy.html')
            for sentence in article_text:
                ret = is_haiku(sentence)
                if ret:
                    print "FOUND HAIKU"
                    return ret

            count += 1
    
    for i in range(5):
        print month_urls[i]
        print month_urls[i] in used_urls

    print 'is used urls'
    print used_urls


def main():

    config = SafeConfigParser()
    script_dir = os.path.dirname(__file__)
    config_file = os.path.join(script_dir, 'settings.cfg')
    config.read(config_file)

    used_urls_csv = config.get('files','used_urls')
    log_file = config.get('files','logfile')

    api_key = config.get('nytimes','api_key')
    year = config.get('nytimes','year')
    month = config.get('nytimes','month')

    #logging.basicConfig(filename=log_file, level=logging.INFO)

    #logging.info("Starting")

    month_urls = ['https://www.nytimes.com/2018/01/02/science/donkeys-africa-china-ejiao.html', 'https://www.nytimes.com/2018/01/02/learning/new-years-resolutions.html', 'https://www.nytimes.com/2018/01/02/health/fake-news-conservative-liberal.html', 'https://www.nytimes.com/2018/01/02/world/asia/kim-jong-un-suit-north-korea.html', 'https://www.nytimes.com/2018/01/02/sports/college-football-playoff-alabama-clemson.html', 'https://www.nytimes.com/2018/01/02/learning/02WODLN.html', 'https://www.nytimes.com/2018/01/02/briefing/iran-north-korea-times-up.html', 'https://www.nytimes.com/2018/01/02/sports/soccer/premier-league-top-six.html', 'https://www.nytimes.com/2018/01/01/pageoneplus/no-corrections-january-2-2018.html', 'https://www.nytimes.com/2018/01/01/todayspaper/quotation-of-the-day-skittish-and-skulking-californias-fire-cats-prove-hard-to-corral.html', 'https://www.nytimes.com/2018/01/01/sports/isaiah-thomas-cavaliers.html', 'https://www.nytimes.com/2018/01/01/crosswords/daily-puzzle-2018-01-02.html', 'https://www.nytimes.com/2018/01/01/business/gretchen-carlson-miss-america.html', 'https://www.nytimes.com/2018/01/01/opinion/the-retreat-to-tribalism.html', 'https://www.nytimes.com/2018/01/01/sports/college-football-playoff-georgia-beats-oklahoma.html', 'https://www.nytimes.com/2018/01/01/opinion/bill-de-blasio-inauguration.html', 'https://www.nytimes.com/2018/01/01/science/ukraine-space-science.html', 'https://www.nytimes.com/2018/01/01/arts/dance/peter-martins-resigns-ballet.html', 'https://www.nytimes.com/2018/01/01/business/dealbook/biggest-deals-2017.html', 'https://www.nytimes.com/2018/01/01/world/americas/brazil-prison-riot.html', 'https://www.nytimes.com/2018/01/01/nyregion/park-or-playground-semantics-dispute-illuminates-preservationists-fight.html', 'https://www.nytimes.com/2018/01/01/nyregion/at-de-blasio-inaugural-speeches-by-two-who-might-replace-him.html', 'https://www.nytimes.com/2018/01/01/nyregion/weather-and-visiting-senator-steal-the-show-at-de-blasio-inauguration.html', 'https://www.nytimes.com/2018/01/01/world/americas/costa-rica-plane-crash.html', 'https://www.nytimes.com/2018/01/01/opinion/ai-and-big-data-could-power-a-new-war-on-poverty.html', 'https://www.nytimes.com/2018/01/01/world/middleeast/israeli-jerusalem-west-bank.html', 'https://www.nytimes.com/2018/01/01/opinion/how-not-to-impeach.html', 'https://www.nytimes.com/2018/01/01/nyregion/metropolitan-diary-meeting-bill-murray.html', 'https://www.nytimes.com/2018/01/01/sports/hockey/winter-classic-rangers-sabres.html', 'https://www.nytimes.com/2018/01/01/science/calestous-juma-african-agriculture-dies.html', 'https://www.nytimes.com/2018/01/01/us/politics/trump-businesses-regulation-economic-growth.html', 'https://www.nytimes.com/2018/01/01/insider/lebanon-palestine-scoop-saad-hariri.html', 'https://www.nytimes.com/2018/01/01/opinion/online-shopping-sales-tax.html', 'https://www.nytimes.com/2018/01/01/opinion/was-america-duped-at-khe-sanh.html']




    #month_urls = get_articles(api_key, year, month)
    used_urls = get_used_urls(used_urls_csv)

    found_haiku = check_haiku(month_urls, used_urls)
    print found_haiku
    

if __name__ == "__main__":
    main()
