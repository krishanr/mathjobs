"""
Notes:
This python script has code for scraping old versions of www.mathjobs.org using
http://web.archive.org/.

Improvement ideas:
* To avoid counting duplicates for multiple
years, use the mathjobs ID #.
* Distinguish between lecturer, tenure-track, postdoc etc.
  positions.
* Apply Git to this repository.
* Be able to use multiple keywords for one topic:
** E.g. geometric analysis, analysis or geometry. Could also look in the plain text of the post.
   Deal with postings that are not specific, so they could be anything. E.g. a job for analysis, geometry etc.

Some assumptions:
* Are all math jobs listed on mathjobs.org?

Possible questions:
* Trends in research tenure-track positions over the last 10 years?
* Trends in teaching tenure-traack positions over the last 10 years?

"""

from bs4 import BeautifulSoup
import copy
from datetime import datetime
import json
import matplotlib.pyplot as plt
import re
import requests
from collections import defaultdict
import os


def links_in_range(deserialized, start, end):
    """Return an iterable of links in the date range
    from start to end.
    """

    for archive in deserialized:
        if ((start <= int(archive[1]) <= end) and archive[2].endswith(":80/")
             and archive[3] == "text/html"   ):
            yield "http://web.archive.org/web/" + archive[1] + "/" + archive[2]
        if int(archive[1]) > end:
            break

def count_keywords(year, key_words):
    count = 0
    #Don't modify the input
    key_words = copy.deepcopy(key_words)
    for link in links_in_range(deserialized, int( str(year) + "0"*10 ), int( str(year+1) + "0"*10 )):
        req = requests.get(link)
        #print("Original link: ", link)
        if req.status_code == requests.codes.ok:
            #The url is working, so first hit view jobs.
            soup = BeautifulSoup(req.text, 'html5lib')
            nav_links = soup('ul', 'nav')
            for li in nav_links[0].find_all('li'):
                if li.text == 'View Jobs':
                    nav_link =  "https://web.archive.org" + li.a['href']
            req2 = requests.get(nav_link)
            if req2.status_code != requests.codes.ok:
                print("Following link didn't work: ", nav_link)
                continue
            count += 1
            soup = BeautifulSoup(req2.text, 'html5lib')
            jobs_link = "https://web.archive.org" + soup.p.find_all('a')[1]['href']
            req3 = requests.get(jobs_link)
            if req3.status_code != requests.codes.ok:
                print("Following link didn't work: ", jobs_link)
                continue
            #print("req3 link", req3.links)
            soup = BeautifulSoup(req3.text, 'html5lib')
            all_paragraphs = soup.find_all('dt')
            #Now find all the <li> items
            for paragraph in all_paragraphs:
                li_items = paragraph.find_all('li')
                for li_item in li_items:
                    try:
                        for i, key_item in enumerate(key_words):
                            if re.search(key_item[0], li_item.text):
                                key_words[i][1] = key_words[i][1] + 1                                     
                    except:
                        print("Something went wrong.")
            break
    return count, key_words

def find_trends(years, key_words):
    """
    Given a list of years, such as 
    years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020],
    and keywords, such as
    key_words = [[r"(?i)mathematical physics", 0]],
    find_trends returns a dictionary of a list of job counts for each year.
    The keys of this dictionary are the keywords.
    
    This is obtained by searching a web archive from the given year for each
    keyword.
    """
    yearly_count = defaultdict(list)
    for year in years:
        _, keywords_with_count = count_keywords(year, key_words)
        for key_word, key_count in keywords_with_count:
            yearly_count[key_word].append(key_count)
    
    return yearly_count

def test_trends():    
    key_words = [[r"(?i)mathematical physics", 0],
             [r"(?i)data science", 0],
             [r"(?i)statistics", 0],
             [r"(?i)algebraic geometry", 0],
             [r"(?i)geometric analysis", 0],
             [r"(?i)analysis", 0],
             [r"(?i)geometry", 0]]

    #Test the key_words match as expected.
    for key_word, _ in key_words:
        assert re.search(key_word, "some text " + key_word + " more text")

    key_word_counts = find_trends(list(range(2010, 2019)), key_words)

    plt.plot(key_word_counts[r"(?i)data science"], label='data science')
    plt.plot(key_word_counts[r"(?i)statistics"], label='statistics')
    plt.plot(key_word_counts[r"(?i)algebraic geometry"], label='alg geometry')
    plt.plot(key_word_counts[r"(?i)geometry"], label='geometry')
    plt.legend()

    plt.show()

timemap_link = "http://web.archive.org/web/timemap/json/http://www.mathjobs.org"
req = requests.get(timemap_link)
if req.status_code == requests.codes.ok:
    #Our data is an array of arrays, which should be
    #deserialized to a python list of lists.
    deserialized = json.loads(req.text)
    assert deserialized[0][4] == "statuscode"
#TODO: handle the case we get another response code...
    
#Remove the header array to avoid errors.
deserialized = deserialized[1:]
deserialized.sort(key =lambda x: int(x[1]))

if __name__ == "__main__":
    test_trends()