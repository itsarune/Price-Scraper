from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import configparser

def search(driver, search_text, search_xpath) :
    search_bar = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, search_xpath)))
    search_bar.clear()
    search_bar.send_keys(search_text)
    search_bar.send_keys(Keys.RETURN)
    return


def find_products(driver, element_xpath) :
    return WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, element_xpath)))


def extract_info(elements, vendor, price, link) :
    products = list()
    for e in elements:
        products.append(
            (e.get_attribute(vendor), e.get_attribute(price),
             e.get_attribute(link))
        )
    return products


def extract_seller_data(driver, config, seller_config) :
    try :
        master_product_list = list()
        driver.get(config[seller_config]["homepage"])
        search(driver, search_item, config[seller_config]["search_xpath"])
        products = extract_info(
            find_products(driver, config[seller_config]["product_xpath"]),
            config[seller_config]["vendor_field"],
            config[seller_config]["price_field"],
            config[seller_config]["link_field"])
        return products
    except Exception as e:
        print("Error with " + seller_config + ". Skipping...")
        print(str(e) + "\n");
        return list()

search_item = "9782014015973"

# options = webdriver.Safari()
# options.add_argument("-headless")

browser = webdriver.Safari()
config = configparser.ConfigParser()
config.read('config.ini')

p1 = extract_seller_data(browser, config, config.sections()[0])
p2 = extract_seller_data(browser, config, config.sections()[1])
p3 = extract_seller_data(browser, config, config.sections()[2])

browser.quit()
#browser.get("http://www.bookscouter.com/buy")

#search(browser, search_item, "//input[@class='input--text input--search']")
#elements = find_products(browser,
#                         "//a[@class='link--buy link--buy--buy btn action']")
#product_info = extract_info(elements, "data-vendor", "data-price", "href")
# search_key = browser.find_element_by_xpath("//button[@class='btn btn--accent search__btn']")
# search_key.click()

#print(product_info)

#try :
#    elements = WebDriverWait(browser, 10).until(
#        EC.presence_of_all_elements_located((By.XPATH, "//a[@class='link--buy link--buy--buy btn action']")))

#    products = list()

#    for e in elements:
#        products.append(
#            (e.get_attribute("data-vendor"), e.get_attribute("data-price"), e.get_attribute("href"))
#        )
#    print(elements)
#    print(products)
#except :
#    print("ERROR! No element found.")

