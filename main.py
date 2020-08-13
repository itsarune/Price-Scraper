from selenium import webdriver
from selenium.common.exceptions import *

options = webdriver.FirefoxOptions()
#options.add_argument("-headless")
options.add_argument("-safe-mode")

browser = webdriver.Firefox(options=options)
browser.get("http://ww.bing.com")