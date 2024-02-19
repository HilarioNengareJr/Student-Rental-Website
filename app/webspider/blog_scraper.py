import json
import time
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium_stealth import stealth
import undetected_chromedriver as uc


def blog_scraper():
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

    try:
        driver.get("https://www.studentrentalslacrosse.com/student-rental-blog/")

        collective_blog = []

        soup = BeautifulSoup(driver.page_source, "lxml")

        articles = soup.select("article.post")

        for article in articles:
            blog = {}

            image_cover = article.find("img")
            blog['Image Cover'] = image_cover['src'] if image_cover else None

            entry_title = article.select_one("h1.entry-title")
            blog['Title'] = entry_title.a.text if entry_title else None
            link = entry_title.a['href']
            blog['Link'] = link

            entry_date = article.select_one("span.entry-date")
            blog['Date'] = entry_date.a.text if entry_date else None

            entry = article.select_one("div.entry-content")
            blog['Content'] = entry.get_text() if entry else None

            driver.get(link)
            author = article.select_one("span.author")
            blog['Author'] = author.a.text if author else None

            collective_blog.append(blog)

        return collective_blog

    except Exception as e:
        print(f'Error occured {e}')


def write_data_to_file(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file)


def run_background_task():
    write_data_to_file('./blog_data.json', blog_scraper())
    time.sleep(1800)
