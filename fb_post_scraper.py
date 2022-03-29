#Selenium + BS4
from selenium import webdriver
from selenium.webdriver.chrome import options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup, element
from main import Utils
import xlsxwriter
import pickle
import time
import re

with open("links.pkl", "rb") as f:
    links = pickle.load(f)
# link_length = len(links)
with open("pagename.txt") as page_file:
    p_name  = page_file.readlines()[0]
workbook = xlsxwriter.Workbook(f'{p_name}_{str(len(links))}.xlsx')
worksheet = workbook.add_worksheet()

firefox_options = Options()
firefox_options.add_argument('--incognito')
firefox_options.add_argument("--headless")  
driver = webdriver.Firefox(options=firefox_options)
driver.get('https://www.facebook.com/')


u = Utils(driver)


with open('credentials.txt') as cred_file:
    creds = cred_file.readlines()
u.fb_login(creds)
time.sleep(5)

driver.maximize_window()

################################################################################
####################################################################################


proxies = u.get_free_proxies()
driver.close()

n_scrolls = 6
SCROLL_HEIGHT = 500

soup = BeautifulSoup()
bold = workbook.add_format({'bold': True})
worksheet.write("A1", "Commenter Name", bold)
worksheet.write("B1", "post", bold)
worksheet.write("C1", "comment", bold)
i = 2
for h, link in enumerate(links):
    time.sleep(5)
    firefox_options = Options()
    firefox_options.add_argument("--headless")  
    if h==len(proxies):
        h=0
    proxy = Proxy({
        'proxyType': ProxyType.MANUAL,
        'httpProxy': proxies[h],
        'ftpProxy': proxies[h],
        'sslProxy': proxies[h],
        'noProxy': ''
    })
    driver = webdriver.Firefox(proxy=proxy,options=firefox_options)
    driver.maximize_window()
    driver.get(link)
    time.sleep(5)
    print(link)
    pg_source = driver.page_source
    soup = BeautifulSoup(pg_source, 'html.parser')
    commenter_names = soup.find_all('div', {"class": "_2b05"})
    all_comments = soup.find_all("div", {"data-sigil": "comment-body"})
    post = soup.find("div", {"class": "msg"})
    for commenter_name, comment in zip(commenter_names, all_comments):
        worksheet.write("A{}".format(i), commenter_name.getText())
        worksheet.write("C{}".format(i), comment.getText())
        try:
            worksheet.write("B{}".format(i), post.getText())
        except:
            pass
        print(i)
        i += 1
    time.sleep(10)
    driver.close()
workbook.close()
