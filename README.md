Textbook Price Scraper

Uses Selenium to scrape website data

# User stories:
    - Pass in a search term and look at search results from multiple websites (reporting source, price and a follow-up
        link)
    - Add more websites using a configuration file

# Config Instructions

- "homepage": website link
- "search_xpath": xpath for the search search bar
- "product_xpath": xpath for finding products
- "vendor_field?", "price_field?", "link_field?": if true, the vendor_field represents a property in "product_xpath", else it is a xpath directly to the field
- "vendor_field", "price_field", "link_field": field property or xpath for the field
- "search_icon": fallback icon for searching products
