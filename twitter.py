from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from bs4 import BeautifulSoup as Soup
import time
import sys


# provide the url here
if len(sys.argv) > 1:
    my_url = "https://twitter.com/" + sys.argv[1]
else:
    my_url = "https://twitter.com/sojoodi"

LIMIT = 100
if len(sys.argv) > 2:
    LIMIT = sys.argv[2]
else:
    LIMIT = 20

path_to_chrome_driver = "./chromedriver"
driver = webdriver.Chrome(executable_path=path_to_chrome_driver)
driver.base_url = my_url
driver.get(driver.base_url)

lastHeight = driver.execute_script("return document.body.scrollHeight")
time.sleep(2)

while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # define how many seconds to wait while dynamic page content loads
    time.sleep(5)
    newHeight = driver.execute_script("return document.body.scrollHeight")

    if newHeight == lastHeight:
        break
    else:
        lastHeight = newHeight

html_source = driver.page_source
source_data = html_source.encode('utf-8')
sp = Soup(source_data, "lxml")


def statnum_parser(soup):
    """
    Takes in soup object then parses it. After parsing fetches number of tweets, followers and following
    of the user provided through the link.
    :param soup:
    :return: dict
    """
    #declared a dictionary
    user_info = {}

    #finds indicated div with the indicated class name
    summary_section = soup.find_all("span", {"class": "ProfileNav-value"})
    full_name = soup.find("a", {"class": "fullname"})
    likes = soup.find_all("span", {"class": "ProfileNav-value"})

    #grabs the content and assigns to dictionary with the respective key name
    user_info["Tweets"] = summary_section[0].text.strip()
    user_info["Following"] = summary_section[1].text
    user_info["Followers"] = summary_section[2].text
    user_info["Full_Name"] = full_name.text.strip()
    user_info["Likes"] = likes[3].text

    return user_info

def detailed_section(soup):
    """
       Takes in soup object then parses it. After parsing fetches tweet id, number of likes,
       number of replies and retweets.
       :param soup:
       :param limit:
       :return: dict
    """
    detailed_info_dict = {}

    # populates the list with the tweet id's
    tweet_ids = []
    stat = statnum_parser(soup)
    name = stat["Full_Name"]
    #print(page_soup.select("div.tweet"))
    for tweet in soup.select("div.tweet"):
        if tweet['data-name'] == name:
            tweet_ids.append(tweet['data-tweet-id'])

    detailed_section_reply = soup.find_all("span", {"class": "ProfileTweet-action--reply"})
    detailed_section_retweet = soup.find_all("span", {"class": "ProfileTweet-action--retweet"})
    detailed_section_likes = soup.find_all("span", {"class": "ProfileTweet-action--favorite"})
    detailed_section_timestamp = soup.find_all("a", {"class": "tweet-timestamp"})
    print(len(tweet_ids))
    if LIMIT <= len(tweet_ids):
        for i in range(0, LIMIT):
            # gets reply number
            reply_count = detailed_section_reply[i].text
            #print(reply_count[:2])

            # gets retweet number
            retweet_count = detailed_section_retweet[i].text
           # print(retweet_count[:2])
            # gets like number
            like_count = detailed_section_likes[i].text
           # print(like_count[:2])
            time = detailed_section_timestamp[i]
            f_time = time["title"]

            # list with above attributes
            my_list = [reply_count.split()[0][0], retweet_count.split()[0][0], like_count.split()[0][0], f_time]

            # add the list as a value to the given tweet id
            detailed_info_dict[tweet_ids[i]] = my_list

    else:
        print("Please choose limit value less than or equal to " + str(len(tweet_ids)))

    return detailed_info_dict

def detailed_section_formatter(soup):
    detailed_section_page = detailed_section(soup)
    for key, value in detailed_section_page.items():
        print("Tweet id: " + str(key) + ", reply count: " + value[0] + ", retweet count: " + value[1] + ", like count: " + value[2] + ", time: " + value[3])

def summary_section_formatter(soup):
    summary_section_page = statnum_parser(soup)
    print("Full Name: " + summary_section_page["Full_Name"] +
          ", total tweets: " + summary_section_page["Tweets"] + ", Following people count: " +
          summary_section_page["Following"] + ", Followers count: " +
          summary_section_page["Followers"] + ", Total like count: " +
          summary_section_page["Likes"] + ", Tweets analyzed: " + str(LIMIT))


summary_section_formatter(sp)
detailed_section_formatter(sp)
