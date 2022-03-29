from selenium import webdriver
from selenium.webdriver.chrome import options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup, element
import argparse
import time
import json
import os
import xlsxwriter
import pickle
from main import Utils

firefox_options = Options()
firefox_options.add_argument('--incognito')
firefox_options.add_argument("--headless")
driver = webdriver.Firefox(options=firefox_options)
driver.get('https://www.facebook.com/')

u = Utils(driver)


with open('credentials.txt') as cred_file:
    creds = cred_file.readlines()
u.fb_logn(creds)

time.sleep(5)

driver.maximize_window()

n_scrolls = 10
SCROLL_HEIGHT = 500

with open("pagename.txt") as page_file:
    p_name  = page_file.readlines()[0]
page_name = p_name
driver.get('https://m.facebook.com/{}/'.format(page_name))  # USER INPUT

BASE_POST_URL = f'https://m.facebook.com/{page_name}/photos/a.'
s = 0
r = SCROLL_HEIGHT
k = 1
elements = []
for h,i in enumerate(range(1, n_scrolls)):
    time.sleep(5)
    try:
        link = driver.find_elements(By.XPATH, "//a[@href]")
        elements.extend(link)
        time.sleep(5)
    except:
        time.sleep(5)
        print("not clicked")
    driver.execute_script("window.scrollTo({},{});".format(str(s), str(r)))
    print(f'scrolled{h}')
    s += SCROLL_HEIGHT
    r += SCROLL_HEIGHT
    time.sleep(2)

post_count = 0
post_links = []
for elem in elements:
    if elem.get_attribute("href").startswith(BASE_POST_URL):
        # print(elem.get_attribute("href"))
        post_links.append(elem.get_attribute("href")[:67+len(page_name)])
        print(post_count)
        post_count += 1


print(post_links)
print(len(post_links))
post_links = list(set(post_links)) # removing duplicates
print(len(post_links))
with open("links.pkl","wb") as f:
    pickle.dump(post_links,f)
