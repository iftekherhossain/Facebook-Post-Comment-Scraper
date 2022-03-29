from seleniumwire import webdriver 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.proxy import Proxy, ProxyType
from bs4 import BeautifulSoup
import random 
import time
from selenium.webdriver.chrome.options import Options
import xlsxwriter
import pickle
from seleniumwire.undetected_chromedriver.v2 import Chrome, ChromeOptions

class Utils:
    def __init__(self,n_scrolls=10):
        chrome_options = Options()
        chrome_options.add_argument('--incognito')
        self.driver = webdriver.Chrome(executable_path="./chromedriver",options=chrome_options)  
        self.driver.request_interceptor = self.interceptor
        self.credential_path = 'credentials.txt'
        self.page_name_path = 'pagename.txt'
        self.n_scrolls = n_scrolls
        self.SCROLL_HEIGHT = 500
        self.elements = []
        self.post_links = []
        self.pickle_path = 'links.pkl'

    def extract_credentials(self):
        with open(self.credential_path) as cred_file:
            self.credendtials = cred_file.readlines()    
        return self.credendtials

    def extract_page_name(self):
        with open(self.page_name_path) as page_file:
            self.p_name  = page_file.readlines()[0]
        return self.p_name

    def extract_links(self,pickle_path):
        self.pickle_path = pickle_path
        with open(self.pickle_path, "rb") as f:
            self.links = pickle.load(f)
        return self.links

    def interceptor(self,request):
        del request.headers['Referer']  # Delete the header first
        request.headers['user-agent']= "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"#Use your current browser header
        request.headers['Referer'] = 'https://www.google.com/'

    def scroll(self,start,end):
        self.driver.execute_script("window.scrollTo({},{});".format(str(start), str(end)))

    def fb_login(self,credentials):
        self.driver.get('https://www.facebook.com/')
        self.driver.maximize_window()
        self.credentials = credentials
        email = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name = 'email']")))
        password = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name = 'pass']")))

        email.clear()
        password.clear()

        email.send_keys(self.credendtials[0][:-1])  # USER INPUT
        password.send_keys(self.credentials[1])  # USER INPUT

        login = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button[type = 'submit']"))).click()
        
        time.sleep(5)
    
    def get_free_proxies(self):
        self.driver.get('https://sslproxies.org')

        table = self.driver.find_element(By.TAG_NAME, 'table')
        thead = table.find_element(
            By.TAG_NAME, 'thead').find_elements(By.TAG_NAME, 'th')
        tbody = table.find_element(
            By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'tr')

        headers = []
        for th in thead:
            headers.append(th.text.strip())

        proxies = []
        for tr in tbody:
            proxy_data = {}
            tds = tr.find_elements(By.TAG_NAME, 'td')
            for i in range(len(headers)):
                proxy_data[headers[i]] = tds[i].text.strip()
            # proxies.append(proxy_data)
            proxy_ip_port = proxy_data['IP Address']+':'+proxy_data['Port']
            proxies.append(proxy_ip_port)
        return proxies

    def colect_links(self,page_name):
        self.page_name = page_name
        s = 0
        r = self.SCROLL_HEIGHT
        print(self.page_name)
        self.driver.get('https://m.facebook.com/{}/'.format(page_name))
        self.driver.maximize_window()
        for h,i in enumerate(range(1, self.n_scrolls)):
            time.sleep(5)
            try:
                link = self.driver.find_elements(By.XPATH, "//a[@href]")
                self.elements.extend(link)
                time.sleep(5)
            except:
                time.sleep(5)
                print("not clicked")
            self.scroll(s,r)
            print(f'scrolled{h}')
            s += self.SCROLL_HEIGHT
            r += self.SCROLL_HEIGHT
            time.sleep(2)
    

    def dump_links(self,page_name):
        self.page_name = page_name
        BASE_POST_URL = f'https://m.facebook.com/{self.page_name}/photos/a.'
        post_count = 0
        for elem in self.elements:
            if elem.get_attribute("href").startswith(BASE_POST_URL):
                # print(elem.get_attribute("href"))
                self.post_links.append(elem.get_attribute("href")[:67+len(self.p_name)])
                print(post_count)
                post_count += 1
        
        print(self.post_links)
        print(len(self.post_links))
        post_links = list(set(self.post_links)) # removing duplicates
        print(len(post_links))
        with open("links.pkl","wb") as f:
            pickle.dump(post_links,f)

    def scraper(self):
        self.driver.maximize_window()
        links = self.extract_links(self.pickle_path)
        workbook = xlsxwriter.Workbook(f'{self.p_name}_{str(len(links))}.xlsx')
        worksheet = workbook.add_worksheet()

        proxies = self.get_free_proxies()
        self.driver.close()

        soup = BeautifulSoup()
        bold = workbook.add_format({'bold': True})
        worksheet.write("A1", "Commenter Name", bold)
        worksheet.write("B1", "post", bold)
        worksheet.write("C1", "comment", bold)
        i = 2
        h=0
        for link in links:
            time.sleep(random.randint(5,8))
            chrome_options = Options()
            chrome_options.add_argument("--headless")  
            driver = webdriver.Chrome(executable_path="./chromedriver",options=chrome_options)
            driver.maximize_window()
            driver.get(link)
            h+=1
            if h==len(proxies)-1:
                h=0
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
            time.sleep(random.randint(5,11))
            driver.close()
        workbook.close()

