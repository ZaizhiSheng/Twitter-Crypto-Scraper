import time

import chromedriver_binary
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webelement import WebElement
#from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import csv
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import pandas as pd

from tonumbers import transfer

max_posts = 20

options = webdriver.ChromeOptions()
options.add_argument("window-size=715,1655")

options.add_argument('--start-maximized')

driver = webdriver.Chrome(options=options)
#driver = webdriver.Chrome(ChromeDriverManager().install())

actions = ActionChains(driver)

header = ['article_text', 'replies', 'retweets', 'love']


def scrollTo(element: WebElement):
    actions.move_to_element(element).perform()


def main(query: str):
    driver.get(
        f"https://mobile.twitter.com/search?q=({query})%20min_replies%3A28%20min_faves%3A99%20min_retweets%3A111&src=typed_query&f=live"
        
    
    )

    driver.implicitly_wait(10)
    post_xpath = '//div[@aria-label="Timeline: Search timeline"]/div/child::div[@style]'

    i = 0
    raw_html_data = []
    data = []
    # posts_elements_uncollected = driver.find_elements('xpath', post_xpath)
    while True:
        try:
            post_element = driver.find_element('xpath', post_xpath + f"[{i + 1}]")
            raw_html_data.append(post_element.get_attribute("innerHTML"))
            actions.move_to_element(post_element).perform()

            time.sleep(2)

            if len(raw_html_data) >= max_posts:
                break
            i += 1
        except NoSuchElementException:
            #print("No element exception")
            posts_elements_uncollected = driver.find_elements('xpath', post_xpath)
            if posts_elements_uncollected:
                actions.move_to_element(posts_elements_uncollected[-1]).perform()
                time.sleep(2)
                i = len(posts_elements_uncollected)-1
            else:
                print("Nothing found.")
                break

    driver.quit()

    for raw_data in raw_html_data:
        soup = BeautifulSoup(raw_data, 'html5lib')
        article_text, replies, retweets, love = "", "", "", ""
        try:
            article_elm = soup.find("article")
            article_text = article_elm.find("div", {'lang': 'en'}).getText()
            reactions = article_elm.find_all("span", {"data-testid": 'app-text-transition-container'})
            replies = transfer(reactions[0].getText())
            retweets = transfer(reactions[1].getText())
            love = transfer(reactions[2].getText())
        except AttributeError:
            print("Attribute Error")

        data.append([article_text, replies, retweets, love])

    with open('data.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        print(data)
        writer.writerows(data)

    # Word Cloud
    print("We are in Word Could now..")

    # Reads 'Youtube04-Eminem.csv' file
    df = pd.read_csv(r"./data.csv", encoding="latin-1")

    comment_words = ''
    stopwords = set(STOPWORDS)

    # iterate through the csv file
    for val in df.article_text:

        # typecaste each val to string
        val = str(val)

        # split the value
        tokens = val.split()

        # Converts each token into lowercase
        for i in range(len(tokens)):
            tokens[i] = tokens[i].lower()

        comment_words += " ".join(tokens) + " "

    wordcloud = WordCloud(width=800, height=800,
                          background_color='white',
                          stopwords=stopwords,
                          min_font_size=10).generate(comment_words)

    # plot the WordCloud image
    plt.figure(figsize=(8, 8), facecolor=None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad=0)

    plt.savefig('word_cloud.png')


if __name__ == '__main__':
    query = "%24NEAR"
    main(query)


