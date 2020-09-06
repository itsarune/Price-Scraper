from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


def search(driver, search_text, search_xpath) :
    search_bar = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, search_xpath)))
    search_bar.clear()
    search_bar.send_keys(search_text)
    search_bar.send_keys(Keys.RETURN)
    return


search_item = "9782014015973"

options = webdriver.FirefoxOptions()
# options.add_argument("-headless")
options.add_argument("-safe-mode")

browser = webdriver.Firefox(options=options)
browser.get("http://www.bookscouter.com/buy")

search(browser, search_item, "//input[@class='input--text input--search']")

# search_key = browser.find_element_by_xpath("//button[@class='btn btn--accent search__btn']")
# search_key.click()

try :
    elements = WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//a[@class='link--buy link--buy--buy btn action']")))

    products = list()

    for e in elements:
        products.append(
            (e.get_attribute("data-vendor"), e.get_attribute("data-price"), e.get_attribute("href"))
        )
    print(elements)
    print(products)
except :
    print("ERROR! No element found.")

