from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import configparser
import selenium.common.exceptions
import traceback

#   Searches the search term on the website
#
# @param WebDriver  : webdriver to search elements
# @param String     : search term
# @param String     : search bar xpath

def search(driver, search_text, search_xpath) :
    search_bar = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, search_xpath)))
    search_bar.clear()
    search_bar.send_keys(search_text)
    search_bar.send_keys(Keys.RETURN)
    return

# Find the products on the website using find_element_by_xpath
#
# @param WebDriver  : WebDriver to complete the search
# @param XPATH      : xpath for the book products
#
# @return the elements found
def find_products(driver, element_xpath) :
    return WebDriverWait(driver, 10).until(
        EC.visibility_of_all_elements_located((By.XPATH, element_xpath)))


# Extracts information from the website based on either the property for the
# product element or directly by xpath
#
# @param Webdriver      : driver to complete the search
# @param List<Elements> : list of elements on the webpage
# @param config         : book config
#
# @return returns a list of products with each product returned as
#   list(vendor, price, link)
def extract_info(driver, elements, config) :
    products = list();
    for i in range(0, len(elements)) :
        try :
            product = list()
            for field in range(0, len(fields)) :
                if (config[fields[field] + "?"] == "true") :
                    product.append(elements[field].get_attribute(config[fields[field]]))
                else :
                    product.append(extract_by_xpath(driver, config[fields[field]], i))
            products.append(product)
        except Exception :
            pass
        # if (config["vendor_field?"] == "true") :
        #     vendor = elements[i].get_attribute(config["vendor_field"])
        # else :
        #     vendor = extract_by_xpath(driver, config["vendor_field"], i)
        # if (config["price_field?"] == "true") :
        #     price = elements[i].get_attribute(config["price_field"])
        # else :
        #     price = extract_by_xpath(driver, config["price_field"], i)
        # if (config["link_field?"] == "true") :
        #     link = elements[i].get_attribute(config["link_field"])
        # else :
        #     link = extract_by_xpath(driver, config["link_field"], i)
        # product = [vendor, price, link]
        # products.append(product)
    return products
    # if ((elements[0].get_attribute(vendor) is None) or
    #     (elements[0].get_attribute(price) is None) or
    #     (elements[0].get_attribute(link) is None)) :
    #      return extract_by_xpath(driver, elements, vendor, price, link)
    # else :
    #      return extract_by_attribute(elements, vendor, price, link)

#

# @deprecated probably
def extract_by_attribute(elements, vendor, price, link) :
    products = list()
    for e in elements :
        products.append((e.get_attribute(vendor),
                         e.get_attribute(price),
                         e.get_attribute(link)))
    return products

# Extract the field information directly by xpath
#
# @param Webdriver : driver where the search was completed
# @param xpath     : xpath element to search for
# @param index     : which element on the list of elements on the webpage that
#                       should be taken
def extract_by_xpath(driver, element_to_look_for, index) :
    elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, element_to_look_for)))
    # print("extract_by_xpath DEBUG: " + elements[index] + '\n')
    return elements[index].text
    # products = list()
    # vendors = WebDriverWait(driver, 10).untli(
    #         EC.presence_of_all_elements_located((By.XPATH, vendor)))
    # print(vendors)
    # prices = WebDriverWait(driver, 10).until(
    #         EC.presence_of_all_elements_located((By.XPATH, price)))
    # links = WebDriverWait(driver, 10).until(
    #         EC.presence_of_all_elements_located((By.XPATH, link)))
    # for i in range (0, len(elements)) :
    #     products.append((vendors[i].text,
    #                     prices[i].text,
    #                     links[i].text))
    # return products

def force_search(driver, search_icon_xpath):
    search = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, search_icon_xpath)))
    search.click()
    return


def extract_seller_data(driver, config, seller_config) :
    try:
        master_product_list = list()
        driver.get(config[seller_config]["homepage"])
        search(driver, search_item, config[seller_config]["search_xpath"])
        try :
            all_product_data = find_products(driver, config[seller_config]["product_xpath"])
        except selenium.common.exceptions.TimeoutException :
            force_search(driver, config[seller_config]["search_icon"])
            all_product_data = find_products(driver, config[seller_config]["product_xpath"])
        products = extract_info(
            driver,
            all_product_data,
            config[seller_config])
        return products
    except selenium.common.exceptions.TimeoutException :
        print("No books found in " + seller_config)
    except Exception as e:
        print("Error with " + seller_config + ". Skipping... Printing stack " +
              "trace: ")
        print(traceback.format_exc())
    return list()


def pricify(price_text) :
    try :
        return int(price_text)
    except Exception :
        try :
            price = str()
            if (price_text[0] == '$') :
                index = 1;
            else :
                index = 0;
            while (price_text[index] != '.') :
                price.join(price_text[index])
                index += 1
            price[index] = "."
            index += 1
            for i in range(1, 2) :
                price.join(price_text[index])
                index += 1;
        except IndexError :
            pass
        if price == '' :
            return 0
        return int(price)

def clean_up_data(product_data) :
    for i in range(0, len(product_data)) :
        price = pricify(product_data[i][1])
        product_data[i][1] = price
    return product_data

search_item = "9782014015973"
fields = ["vendor_field", "price_field", "link_field"]

# options = webdriver.Safari()
# options.add_argument("-headless")

browser = webdriver.Safari()
config = configparser.ConfigParser()
config.read('config.ini')

all_products = list()
for seller_config in config.sections() :
    products_in_seller = extract_seller_data(browser, config, seller_config)
    all_products = all_products + products_in_seller

print("Press enter to end program")
input()

browser.quit()

clean_up_data(all_products)
print(all_products)

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
