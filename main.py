from selenium import webdriver
from selenium.common.exceptions import *

search_item = "9782014015973"

options = webdriver.FirefoxOptions()
#options.add_argument("-headless")
options.add_argument("-safe-mode")

browser = webdriver.Firefox(options=options)
browser.get("http://www.bookscouter.com/buy")

search_bar = browser.find_element_by_xpath("//input[@class='input--text input--search']")
search_bar.send_keys(search_item)
search_key = browser.find_element_by_xpath("//button[@class='btn btn--accent search__btn']")
search_key.click()


item_prices = browser.find_elements_by_class_name('price__price-link')
item_links = browser.find_elements_by_xpath("//a[@class='link--buy link--buy--buy btn action']")

print("Length of item_links: " + str(len(item_links)))

my_links = list()
for href in item_links :
    my_links.append(href.text)
print(my_links)