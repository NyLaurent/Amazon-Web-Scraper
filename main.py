from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import pandas as pd

# Set up Chrome driver on each
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1920x1080')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Function to get product info
def get_product_info(url):
    driver.get(url)
    time.sleep(2)  # Add a delay of 2 seconds
    soup = BeautifulSoup(driver.page_source, "html.parser")

    title_element = soup.select_one("#productTitle")
    title = title_element.text.strip() if title_element else None

    price_element = soup.select_one('span.a-offscreen')
    price = price_element.text if price_element else None

    rating_element = soup.select_one("#acrPopover")
    rating_text = rating_element.attrs.get("title") if rating_element else None
    rating = rating_text.replace("out of 5 stars", "") if rating_text else None

    image_element = soup.select_one("#landingImage")
    image = image_element.attrs.get("src") if image_element else None

    description_element = soup.select_one("#productDescription")
    description = description_element.text.strip() if description_element else None

    # Return product details only if title and price are available
    if title and price:
        return {
            "title": title,
            "price": price,
            "rating": rating,
            "image": image,
            "description": description,
            "url": url
        }
    return None

# Function to parse listing
def parse_listing(listing_url):
    driver.get(listing_url)
    time.sleep(2)  # Add a delay of 2 seconds
    soup_search = BeautifulSoup(driver.page_source, "html.parser")
    link_elements = soup_search.select("[data-asin] h2 a")
    page_data = []

    for link in link_elements:
        product_url = "https://www.amazon.com" + link.attrs.get("href")
        print(f"Scraping product from {product_url[:100]}", flush=True)
        product_info = get_product_info(product_url)
        if product_info:
            page_data.append(product_info)

    # Handle pagination
    next_page_el = soup_search.select_one('a.s-pagination-next')
    if next_page_el:
        next_page_url = "https://www.amazon.com" + next_page_el.attrs.get('href')
        print(f'Scraping next page: {next_page_url}', flush=True)
        page_data += parse_listing(next_page_url)

    return page_data

# Main function
def main():
    search_term = input("Enter the search term: ")
    category_id = input("Enter the Amazon category ID (optional): ")

    if category_id:
        search_url = f"https://www.amazon.com/s?k={search_term}&rh=n%3A{category_id}&ref=nb_sb_noss"
    else:
        search_url = f"https://www.amazon.com/s?k={search_term}&ref=nb_sb_noss"

    data = parse_listing(search_url)

    df = pd.DataFrame(data)
    filename = f"{search_term.replace(' ', '_')}.csv"
    df.to_csv(filename, index=False)
    print(f"Results saved to {filename}")

if __name__ == '__main__':
    main()
