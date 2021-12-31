from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import configparser
import selenium.common.exceptions
import traceback, logging
import csv
import requests

LOG_LEVEL = logging.DEBUG
DEFAULT_CURRENCY = "CAD"

usd_to_cad_exchange_rate = None

# Searches the search term on the website
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
# @param config_name    : book config name
# @param configuration  : configurations
#
# @return returns a list of products with each product returned as
#   list(vendor, price, link)
def extract_info(driver, elements, config_name, configuration) :
	config = configuration[config_name]
	logger = logging.getLogger(config_name)
	logger.debug("extract_info: # of elements: " + str(len(elements)))
	products = list()
	for i in range(0, len(elements)) :
		try :
			product = list()
			for field in range(0, len(fields)) :
				if (config[fields[field] + "_field?"] == "true") :
					product.append(elements[i].get_attribute(config[fields[field] + "_field"]))
				else :
					product.append(extract_by_xpath(configuration, config_name, driver, fields[field], i))
			products.append(product)
		except Exception as ex:
			logger.debug("extract_info: exception encountered: " + traceback.format_exc())
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
def extract_by_xpath(configuration, config_name, driver, element_to_look_for, index) :
	config = configuration[config_name]
	logging.getLogger(config_name).debug("extract_by_xpath: element: " + str(element_to_look_for) + ", at index: " 
										 + str(index))
	elements = WebDriverWait(driver, 10).until(
		EC.presence_of_all_elements_located((By.XPATH, config[element_to_look_for + "_xpath"])))
	logging.getLogger(config_name).debug("extract_by_xpath: number of elements found = " + str(len(elements)))
	# print("extract_by_xpath DEBUG: " + elements[index] + '\n')
	val = elements[index].get_attribute(config[element_to_look_for + "_field"])
	if val is None :
		return elements[index].text
	else :
		return val
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
	logger.debug("force_search: found search button, clicking")
	search.click()
	return


def extract_seller_data(driver, config, seller_config) :
	logger = logging.getLogger(seller_config)
	try:
		master_product_list = list()
		driver.get(config[seller_config]["homepage"])
		search(driver, search_item, config[seller_config]["search_xpath"])
		try :
			all_product_data = find_products(driver, config[seller_config]["product_xpath"])
		except selenium.common.exceptions.TimeoutException :
			logger.debug("Normal search failed, trying with search icon")
			force_search(driver, config[seller_config]["search_icon"])
			all_product_data = find_products(driver, config[seller_config]["product_xpath"])
		products = extract_info(
			driver,
			all_product_data,
			seller_config,
			config)
		return products
	except selenium.common.exceptions.TimeoutException :
		print("No books found in " + seller_config)
	except Exception as e:
		print("Error with " + seller_config + ". Skipping... Printing stack " +
			  "trace: ")
		print(traceback.format_exc())
	return list()


def pricify(price_text) :
	logger.debug("pricify: price_text=" + str(price_text))
	convert_from_us = False
	global usd_to_cad_exchange_rate
	if (usd_to_cad_exchange_rate is None) :
		usd_to_cad_exchange_rate = get_exchange_rate()
		logger.info("USD to CAD exchange rate: " + str(usd_to_cad_exchange_rate))
	try :
		return float(price_text)
	except ValueError :
		index = 0
		price = str()
		try :
			if (price_text.find('US') != -1) :
				index += 2
				convert_from_us = True
			if (price_text[index] == '$') :
				index += 1
			while (price_text[index] == ' ') :
				index += 1
			while (price_text[index] != '.') :
				price += price_text[index]
				index += 1
			price += "."
			index += 1
			for i in range(1, 2) :
				price += (price_text[index])
				index += 1;
		except IndexError :
			pass
		if price == '' :
			return 0
		if convert_from_us :
			price *= usd_to_cad_exchange_rate
		try :
			return float(price)
		except ValueError :
			return 0
	except TypeError :
		return 0
	
def clean_up_data(product_data) :
	for i in range(0, len(product_data)) :
		price = pricify(product_data[i][1])
		product_data[i][1] = price
	return product_data

def output_to_csv(products) :
	with open('output.csv', 'w', newline='') as csvfile :
		reader = csv.writer(csvfile, delimiter=',')
		reader.writerow(['VENDOR', 'PRICE', 'LINK'])
		for product in products :
			reader.writerow(product)
			
def get_exchange_rate(base='USD', target=DEFAULT_CURRENCY) :
	api_uri = "https://api.fixer.io/latest?base={}&symbols={}".format(base, target)
	api_response = requests.get(api_uri)
	
	if (api_response.status_code == 200) :
		return api_response.json()["rates"][target_currency]
	return 1
		

logging.basicConfig()
logger = logging.getLogger('__main__')
logger.setLevel(LOG_LEVEL)

search_item = "9781368021425"
fields = ["vendor", "price", "link"]

# TODO: when system is working, re-enable this so that the browser isn't opened up
# options = webdriver.Safari()
# options.add_argument("-headless")

browser = webdriver.Safari()
config = configparser.ConfigParser()
config.read('config.ini')

all_products = list()
for seller_config in config.sections() :
	logging.getLogger(seller_config).setLevel(LOG_LEVEL)
	products_in_seller = extract_seller_data(browser, config, seller_config)
	logger.info("Books found in " + seller_config + ": " + str(products_in_seller))
	if ((len(products_in_seller) >= 1) and 
		(products_in_seller[0] != None)) :
		all_products = all_products + products_in_seller

print("Press enter to end program")
input()

browser.quit()

clean_up_data(all_products)
output_to_csv(all_products)
print(all_products)
