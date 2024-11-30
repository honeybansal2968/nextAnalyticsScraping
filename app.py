import os
import random
import time
import pandas as pd
from fastapi import FastAPI, HTTPException
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.driver_cache import DriverCacheManager
from selenium.webdriver.common.by import By
from fake_headers import Headers
from fastapi.middleware.cors import CORSMiddleware
import logging
from selenium_driverless import webdriver as webdriverless

proxy_username="ockzoweb"
proxy_password="23wxmulibzuq"
proxy_address="198.23.239.134"
proxy_port="6540"

proxy_url=f"http://{proxy_username}:{proxy_password}@{proxy_address}:{proxy_port}"
seleniumwire_options = {
    "proxy": {
        "http": proxy_url,
        "https": proxy_url,
    }
}
# Initialize FastAPI
app = FastAPI(
    debug=True,
    title="NextAnalytics Server",
    consumes=["application/x-www-form-urlencoded", "multipart/form-data"],
    docs_url='/swagger'
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup ChromeDriver and Selenium
# custom_wdm_cache = os.path.join(os.getcwd(), 'custom_wdm_cache')
# os.environ['WDM_LOCAL'] = custom_wdm_cache

# Setup logging
logging.basicConfig(level=logging.INFO)

def setup_chromedriver():
    logging.info("Setting up ChromeDriver...")
    # custom_wdm_cache = os.path.join(os.getcwd(), 'custom_wdm_cache')
    # os.environ['WDM_LOCAL'] = custom_wdm_cache
    # cache_manager = DriverCacheManager(custom_wdm_cache)
    # os.chmod(custom_wdm_cache, 0o755)  # Ensure proper permissions
    # path = ChromeDriverManager(cache_manager=cache_manager).install()
    path = ChromeDriverManager().install()
    os.chmod(path, 0o755)  # Ensure ChromeDriver is executable
    logging.info(f"ChromeDriver path: {path}")
    return path

# Setup headless Chrome options
# Define a custom user agent
# my_user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0"

my_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"

# capabilities = webdriver.DesiredCapabilities.FIREFOX
# proxy = None
browser_option = Options()
browser_option.add_argument("--headless")  # Running in headless mode (no GUI)
browser_option.add_argument("--no-sandbox")
browser_option.add_argument("--disable-dev-shm-usage")
browser_option.add_argument("--ignore-certificate-errors")
# browser_option.binary_location = '/usr/bin/firefox'
# browser_option.binary_location = r'C:\Users\HP\.cache\selenium\firefox\win64\133.0\firefox.exe'
# browser_option.add_argument("--disable-gpu")
# browser_option.add_argument("--log-level=3")
# browser_option.add_argument("--disable-notifications")
# browser_option.add_argument("--disable-popup-blocking")
browser_option.add_argument(f"--user-agent={my_user_agent}")

# if proxy:
#     browser_option.add_argument(f"--proxy-server={proxy}")


# Setup WebDriver
driver_path = setup_chromedriver()
service = Service(executable_path=driver_path)
driver = webdriver.Chrome(service=service, options=browser_option,)
# actions = ActionChains(driver)

def getSearchPostData(search_keyword, index, name="", forCompetitorAnalysis=False):
    # Navigate to the search results page
    url = f'https://www.reddit.com/search/?q={search_keyword}'
    driver.get(url)
    time.sleep(3)  # Consider using WebDriverWait instead of sleep for better reliability
    logging.info("Navigated to search page.")

    posts_data = []
    list_length = 0  # posts count
    try:
        if forCompetitorAnalysis:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
        post_cards = driver.find_elements(By.CSS_SELECTOR, 'a[data-testid="post-title-text"]')
        post_cards_1 = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="search-counter-row"]')
        post_cards_2 = driver.find_elements(By.CSS_SELECTOR, 'faceplate-timeago')
        logging.info(f"Found {len(post_cards)} post cards.")

        idx = list_length
        for card in post_cards_1:
            try:
                votes_count = card.find_element(By.XPATH, './/faceplate-number').text
                comments_count = card.find_element(By.XPATH,
                    './/span[contains(text(), "comment") or contains(text(), "comments")]/preceding-sibling::faceplate-number'
                ).text
                posts_data.append({
                    "index": idx,
                    "comment_count": comments_count,
                    "votes_count": votes_count
                })
                idx += 1
            except Exception as e:
                logging.error(f"Error processing post_card_1: {e}")

        idx = list_length
        for card in post_cards:
            try:
                url = card.get_attribute("href")
                title = card.text
                posts_data[idx]["title"] = title
                posts_data[idx]["url"] = url
                idx += 1
            except Exception as e:
                logging.error(f"Error processing post_cards: {e}")
        
        idx = list_length
        for card in post_cards_2:
            try:
                time_element = card.find_element(By.XPATH, './time')
                post_time = time_element.get_attribute('datetime')
                posts_data[idx]["time"] = post_time
                idx += 1
            except Exception as e:
                logging.error(f"Error processing post_cards_2: {e}")
    except Exception as e:
        logging.error(f"Error in scrolling or extracting data: {e}")

    df = pd.DataFrame(posts_data)
    df.to_csv(f'posts_data_{index}.csv', index=False)
    logging.info(f"Data saved to posts_data_{index}.csv")
    return df

def get_webpage_title(url: str) -> str:
    try:
        getSearchPostData(search_keyword="migraine", index=0)
        url="https://www.reddit.com"
        driver.get(url)
        title = driver.title
        logging.info(f"Page title: {title}")
        return title
    except Exception as e:
        logging.error(f"Error fetching webpage title: {e}")
        return str(e)

@app.get("/")
async def home():
    return {"message": "Hello"}

@app.get("/get-title/")
async def fetch_title(url: str):
    """
    Fetch the title of a webpage by URL.
    Example: /get-title/?url=https://www.reddit.com
    """
    try:
        title = get_webpage_title(url)
        return {"url": url, "title": title}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# @app.get("/get-reddit/")
# async def getReddit(url: str):
#     """
#     Fetch the title of a webpage by URL.
#     Example: /get-title/?url=https://www.reddit.com
#     """
#     try:
#         options = webdriverless.ChromeOptions()
#         driver_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"

#         options.add_argument("--headless")  # Running in headless mode (no GUI)
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.add_argument("--ignore-certificate-errors")
#         options.add_argument(f"--user-agent={driver_agent}")

#         title="Notitle"
#         async with webdriverless.Chrome(options=options) as driver:
#             await driver.get('https://www.reddit.com')
#             time.sleep(3)

#             title = await driver.title
#             url = await driver.current_url
#             source = await driver.page_source
#             print(title)
#             return {"url": url, "title": title}
#         return {"url": url, "title": title}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# Run the app
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=7860)

# from selenium import webdriver
# from flask import Flask, request
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.proxy import Proxy, ProxyType
# app = Flask(__name__)

 
# def download_selenium():
#     prox = Proxy()
#     prox.proxy_type = ProxyType.MANUAL
#     prox.http_proxy = "ip_addr:port"
#     prox.socks_proxy = "ip_addr:port"
#     prox.ssl_proxy = "ip_addr:port"
#     chrome_options = webdriver.ChromeOptions()
#     driver_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
#     capabilities = webdriver.DesiredCapabilities.CHROME
#     prox.to_capabilities(capabilities)
#     chrome_options.add_argument("--headless=new")
#     # chrome_options.add_argument(f"--proxy-server={proxy}")
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")
#     # chrome_options.add_argument("--ignore-certificate-errors")
#     # chrome_options.add_argument("--disable-gpu")
#     # chrome_options.add_argument("--log-level=3")
#     # chrome_options.add_argument("--disable-notifications")
#     # chrome_options.add_argument("--disable-popup-blocking")
#     prefs = {"profile.managed_default_content_settings.images": 2}
#     # chrome_options.add_experimental_option("prefs", prefs)
#     chrome_options.add_argument(f"--user-agent={driver_agent}")
#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install(),desired_capabilities=capabilities), options=chrome_options)
#     driver.get("https://reddit.com")
#     title = driver.title
#     # language = driver.find_element(By.XPATH, "//div[@id='SIvCob']").text
#     data = {'Page Title': title}
#     return data


# @app.route('/', methods = ['GET','POST'])
# def home():
#     if (request.method == 'GET'):
#         return download_selenium()


# if __name__ == "__main__":
#     app.run(debug=True, port=3000)
