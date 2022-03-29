from main import Utils

number_of_scrolls = int(input("How many pages do you want to scroll?\n"))
u = Utils(number_of_scrolls)
print("collecting links...")
credentials = u.extract_credentials()
page_name = u.extract_page_name()
u.fb_login(credentials)
u.colect_links(page_name)
u.dump_links(page_name)
print("Start Scraping....")
u.scraper()