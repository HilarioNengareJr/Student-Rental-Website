import time
import json
import random
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from typing import Dict
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager

def estate_scraper(url):
    options = uc.ChromeOptions()
    options.headless = True
    options.add_argument("start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = uc.Chrome(options=options)

    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True
            )

    collective_data = []

    try:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "lxml")

        divs = soup.select('div.list-item')

        for div in divs:
            retrieved_data = {}

            agent_name_element = div.find("div", class_="broker-name")
            if agent_name_element:
                agent_name = agent_name_element.find("p").text
                retrieved_data['Agent Name'] = agent_name
            else:
                retrieved_data['Agent Name'] = None

            price_element = div.find("p", class_="price")
            if price_element:
                price = price_element.text.strip()
                retrieved_data['Price'] = price
            else:
                retrieved_data['Price'] = None

            link_element = div.find("a", class_="stretched-link")
            if link_element:
                listing_title = link_element.text.strip()
                retrieved_data['Listing Title'] = listing_title
                location = link_element.find("span").text.strip()
                retrieved_data['Location'] = location
            else:
                retrieved_data['Listing Title'] = None
                retrieved_data['Location'] = None

            phone_number_element = div.find("a", class_="btn-call")
            if phone_number_element:
                phone_number = phone_number_element["data-phone"]
                retrieved_data['Phone Number'] = phone_number
            else:
                retrieved_data['Phone Number'] = None

            stretched_link_element = div.find("a", class_="stretched-link")
            if stretched_link_element:
                stretched_link = stretched_link_element["href"]
                print(f"Stretched Link: {stretched_link}")

                driver.get("https://www.hangiev.com" + stretched_link)
                link_soup = BeautifulSoup(driver.page_source, "lxml")

                room_details_div = link_soup.find(
                    'div', class_='item-rooms-detail')
                if room_details_div:
                    room_details = [detail.text.strip()
                                    for detail in room_details_div.find_all('div')]
                    retrieved_data['Room Details'] = room_details

                list_element = link_soup.find('ul', class_='item-table-strong')
                if list_element:
                    list_items = list_element.find_all('li')
                    for item in list_items:
                        label = item.contents[0].strip()
                        value = item.find('span').text.strip()
                        retrieved_data[label] = value

                description = link_soup.find_all(
                    'div', class_='item-detail-box')[1]
                text_content = description.get_text()
                retrieved_data['Description'] = text_content
                print(text_content)

                date_posted_element = link_soup.find(
                    'div', class_='item-stat-box').find('div').find('p').strong.text.strip()
                retrieved_data['Last Updated'] = date_posted_element
                print(date_posted_element)

                list_element = link_soup.find('ul', class_='item-table-score')
                if list_element:
                    items = list_element.find_all('li')
                    outside_features = []

                    for item in items:
                        location_element = item.find('div')
                        distance_element = item.find('span')

                        if location_element and distance_element:
                            location = location_element.text.strip()
                            distance = distance_element.text.strip()

                            outside_features.append(
                                {'Location': location, 'Distance': distance})

                    retrieved_data['Outside Features'] = outside_features

                agency_info = link_soup.find('div', class_='agency-info')
                if agency_info:
                    image_tag = agency_info.find(
                        'img', class_='rounded-circle')
                    if image_tag:
                        retrieved_data['Agent Image'] = image_tag['src']
                    else:
                        retrieved_data['Agent Image'] = None
                else:
                    retrieved_data['Agent Image'] = None

                component = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, 'p[data-toggle="modal"][data-target="#itemTabs"][data-tab="tabs-photo"]')))
                component.click()
                time.sleep(2)
                image_urls_list = []
                div_blocks = link_soup.find_all("div", class_='photo-cont')
                for div in div_blocks:
                    image_tag = div.find('img', class_="img-fluid")['data-src']
                    print(image_tag)
                    image_urls_list.append(image_tag)
                retrieved_data['Images'] = image_urls_list

                collective_data.append(retrieved_data)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

    return collective_data


def write_data_to_file(filename: str, data: Dict) -> None:
    for key, value in data.items():
        random.shuffle(value)

    with open(filename, 'w') as file:
        json.dump(data, file)


def background_task() -> None:
    while True:
        with ThreadPoolExecutor() as executor:
            rent_data = executor.submit(
                estate_scraper, 'https://www.hangiev.com/north-cyprus-properties-for-rent').result()
            cyprus_data = executor.submit(
                estate_scraper, 'https://www.hangiev.com/north-cyprus-properties-for-sale').result()
            iskele_data = executor.submit(
                estate_scraper, 'https://www.hangiev.com/kyrenia-properties-for-rent').result()
            magusa_data = executor.submit(
                estate_scraper, 'https://www.hangiev.com/famagusta-properties-for-rent').result()
            konut_data = executor.submit(
                estate_scraper, 'https://www.hangiev.com/famagusta-properties-for-sale').result()
            featured_data = executor.submit(
                estate_scraper, 'https://www.hangiev.com/iskele-properties-for-rent').result()
            lefke_data = executor.submit(
                estate_scraper, 'https://www.hangiev.com/nicosia-properties-for-sale').result()
            guzelyurt_data = executor.submit(
                estate_scraper, 'https://www.hangiev.com/nicosia-properties-for-rent').result()
            sale_data_1 = executor.submit(
                estate_scraper, 'https://www.hangiev.com/kyrenia-properties-for-sale').result()
            sale_data_2 = executor.submit(
                estate_scraper, 'https://www.hangiev.com/iskele-properties-for-sale').result()
            sale_data_3 = executor.submit(
                estate_scraper, 'https://www.hangiev.com/lefke-properties-for-rent').result()
            sale_data_4 = executor.submit(
                estate_scraper, 'https://www.hangiev.com/lefke-properties-for-sale').result()

        all_data = {
            'featured_data': featured_data,
            'lefke_data': lefke_data,
            'guzelyurt_data': guzelyurt_data,
            'rent_data': rent_data,
            'cyprus_data': cyprus_data,
            'iskele_data': iskele_data,
            'magusa_data': magusa_data,
            'konut_data': konut_data,
            'sale_data_1': sale_data_1,
            'sale_data_2': sale_data_2,
            'sale_data_3': sale_data_3,
            'sale_data_4': sale_data_4
        }

        write_data_to_file('./estate_data.json', all_data)

        time.sleep(1800)
