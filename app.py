import os
import random
import time
import pandas as pd
from fastapi import FastAPI, HTTPException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.driver_cache import DriverCacheManager
from selenium.webdriver.common.by import By
from fake_headers import Headers
from fastapi.middleware.cors import CORSMiddleware
import logging
from pyppeteer import launch
import asyncio

# from selenium_driverless import webdriver as webdriverless


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
    # logging.info("Setting up ChromeDriver...")
    custom_wdm_cache = os.path.join(os.getcwd(), 'custom_wdm_cache')
    os.environ['WDM_LOCAL'] = custom_wdm_cache
    cache_manager = DriverCacheManager(custom_wdm_cache)
    os.chmod(custom_wdm_cache, 0o755)  # Ensure proper permissions
    path = ChromeDriverManager(cache_manager=cache_manager).install()
    # path = GeckoDriverManager(cache_manager=cache_manager).install()
    os.chmod(path, 0o755)  # Ensure ChromeDriver is executable
    logging.info(f"ChromeDriver path: {path}")
    return path

# Setup headless Chrome options
# Define a custom user agent
# my_user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0"
header = Headers().generate()["User-Agent"]
# my_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"

# capabilities = webdriver.DesiredCapabilities.CHROME
# proxy = None
browser_option = Options()
# browser_option..level = 'trace'
browser_option.add_argument("--headless")  # Running in headless mode (no GUI)
browser_option.add_argument("--no-sandbox")
browser_option.add_argument("--disable-dev-shm-usage")
browser_option.add_argument("--disable-blink-features=AutomationControlled")

browser_option.add_argument("--ignore-certificate-errors")
# profile = webdriver.FirefoxProfile()
# profile.set_preference("general.useragent.override", "Your User Agent String")
# browser_option.profile = profile
logging.info(f"browser_version: {browser_option.browser_version}")
# browser_option.set_capability(
    
# )
#     name="",
#     value=capabilities)
# browser_option.capabilities = {
#     "moz:firefoxOptions": {
#         "args": [
#             "--headless",
#             "--no-sandbox",
#             "--disable-dev-shm-usage",
#             "--ignore-certificate-errors",
#             f"--user-agent={header}"
#         ]
#     }
# }
# browser_option.binary_location = '/usr/bin/firefox'
# browser_option.binary_location = r'C:\Users\HP\.cache\selenium\firefox\win64\133.0\firefox.exe'
# browser_option.add_argument("--disable-gpu")
# browser_option.add_argument("--log-level=3")
# browser_option.add_argument("--disable-notifications")
# browser_option.add_argument("--disable-popup-blocking")
# browser_option.add_argument(f"--user-agent={my_user_agent}")
browser_option.add_argument("--user-agent={}".format(header))

# if proxy:
#     browser_option.add_argument(f"--proxy-server={proxy}")


# Setup WebDriver
driver_path = setup_chromedriver()
service = Service(executable_path=driver_path)
driver = webdriver.Chrome(service=service, options=browser_option)
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

def getPinterestSearchPostData(search_keyword, index, name="", forCompetitorAnalysis=False):
    # Navigate to the search results page
    url = f'https://www.pinterest.com/search/pins?q={search_keyword}'
    driver.get(url)
    driver.implicitly_wait(5)  # Consider using WebDriverWait instead of sleep for better reliability
    logging.info("Navigated to search page.")
    # links = driver.find_elements(By.CSS_SELECTOR, "div[data-test-id='related-pins-title']")
    # print("links", links)
    posts_data = []
    list_length = 0  # posts count
    
    try:
        if forCompetitorAnalysis:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
        post_cards = driver.find_elements(By.CSS_SELECTOR, "div[data-test-id='related-pins-title']")
        # post_cards_1 = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="search-counter-row"]')
        # post_cards_2 = driver.find_elements(By.CSS_SELECTOR, 'faceplate-timeago')
        logging.info(f"Found {len(post_cards)} post cards.")

        # idx = list_length
        # for card in post_cards_1:
        #     try:
        #         votes_count = card.find_element(By.XPATH, './/faceplate-number').text
        #         comments_count = card.find_element(By.XPATH,
        #             './/span[contains(text(), "comment") or contains(text(), "comments")]/preceding-sibling::faceplate-number'
        #         ).text
        #         posts_data.append({
        #             "index": idx,
        #             "comment_count": comments_count,
        #             "votes_count": votes_count
        #         })
        #         idx += 1
        #     except Exception as e:
        #         logging.error(f"Error processing post_card_1: {e}")

        idx = 0
        for card in post_cards:
            try:
                title = card.find_element(By.XPATH,
                    './/div'
                ).text
                # posts_data[idx]["title"] = title
                print("title", title)
                # idx += 1
            except Exception as e:
                logging.error(f"Error processing post_cards: {e}")
        
        # idx = list_length
        # for card in post_cards_2:
        #     try:
        #         time_element = card.find_element(By.XPATH, './time')
        #         post_time = time_element.get_attribute('datetime')
        #         posts_data[idx]["time"] = post_time
        #         idx += 1
        #     except Exception as e:
        #         logging.error(f"Error processing post_cards_2: {e}")
   
    except Exception as e:
        logging.error(f"Error in scrolling or extracting data: {e}")

    df = pd.DataFrame(posts_data)
    df.to_csv(f'posts_data_{index}.csv', index=False)
    logging.info(f"Data saved to posts_data_{index}.csv")
    return df

def get_webpage_title(url: str) -> str:
    try:
        # getSearchPostData(search_keyword="migraine", index=0)
        getPinterestSearchPostData(search_keyword="watercolor art",index=0)
        driver.get(url)
        time.sleep(3)
        title = driver.title
        logging.info(f"Page title: {title}")
        return title
    except Exception as e:
        logging.error(f"Error fetching webpage title: {e}")
        return str(e)

@app.get("/")
async def home():
    return {"message": "Hello"}

async def pupFcuntin(url)->str:
    browser = await launch(
        options={
            'headless': True,
            'args': [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled',
            ],
            # 'executablePath': 'usr/bin/google-chrome',
            # 'executablePath': r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            'executablePath': r'Application\chrome.exe',
        }
    )
    page = await browser.newPage()
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36')
    # Pretend to be a real browser
    await page.evaluateOnNewDocument(
        """
        () => {
            Object.defineProperty(navigator, 'webdriver', { get: () => false });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
        }
        """
    )
    await page.goto(url, options={'waitUntil': 'domcontentloaded'})
    time.sleep(3)
    ## Get HTML
    html = await page.title()
    await browser.close()
    logging.info(f"Page title: {html}")
    return html
@app.get("/puppeteerTrial")
async def puppeteerTrial(url: str):
    html =await pupFcuntin(url)
    return {"message": html}

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



# import os
# from flask import Flask, request, jsonify
# from selenium import webdriver
# from selenium.webdriver.firefox.service import Service
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.firefox import GeckoDriverManager
# import time
# import random

# app = Flask(__name__)

# def setup_driver():
#     """Set up Chrome WebDriver with appropriate options for headless browsing."""
#     chrome_options = Options()
#     # chrome_options.add_argument("--headless")
#     # chrome_options.add_argument("--incognito")
#     # chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#     # chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     # chrome_options.add_experimental_option('useAutomationExtension', False)
#     chrome_options.add_argument("--start-maximized")
#     chrome_options.add_argument("--no-sandbox")
#     # chrome_options.add_argument("--disable-dev-shm-usage")
#     # chrome_options.add_argument("--disable-extensions")
#     # chrome_options.add_argument("--disable-gpu")
#     chrome_options.binary_location = r'C:\Users\HP\.cache\selenium\firefox\win64\133.0\firefox.exe'
#     # chrome_options.binary_location = r'C:\Program Files\Google\Chrome\Application\chrome.exe'

    
#     # service = Service(GeckoDriverManager().install())
#     service = Service(executable_path=r'C:\Users\HP\.cache\selenium\geckodriver\win64\0.35.0\geckodriver.exe')
    
#     driver = webdriver.Firefox(service=service, options=chrome_options)
#     return driver

# def reddit_login_and_scrape(username, password, subreddit):
#     """
#     Log into Reddit and scrape posts from a specified subreddit.
    
#     Args:
#         username (str): Reddit username
#         password (str): Reddit password
#         subreddit (str): Name of the subreddit to scrape
    
#     Returns:
#         list: List of dictionaries containing scraped post information
#     """
#     driver = setup_driver()
#     posts = []
    
#     try:
#         # Navigate to Reddit login page
#         driver.get("https://www.reddit.com/login/")
        
#         # Wait for login form to load
#         WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.ID, "login-username"))
#         )
        
#         # Find and fill in login credentials
#         username_field = driver.find_element(By.ID, "login-username")
#         password_field = driver.find_element(By.ID, "login-password")
        
#         username_field.send_keys(username)
#         password_field.send_keys(password)
        
#         # Submit login form
#         # login_button = driver.find_element(By.XPATH, "//button[@type='button']")
#         # login_button.click()
#         # Find login button using complex selector
#         # login_button=driver.find_element(By.CSS_SELECTOR, 'faceplate-tracker[action="click]')
#         # login_button = WebDriverWait(driver, 4).until(
#         #     EC.element_to_be_clickable((By.XPATH, "//*[@id='login']/auth-flow-modal/div[2]/faceplate-tracker/button"))
#         # )
#         # driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
#         # time.sleep(random.uniform(1, 2))
#         # login_button.click()
#         # Locate the button using XPath with visible text
#         cookies = driver.get_cookies()

#         auth_token = None

#         for cookie in cookies:
#             if cookie["name"] == "auth_token":
#                 auth_token = cookie["value"]
#                 break
#         print("auth_token", auth_token)
#         # wait = WebDriverWait(driver, 10)
#         # login_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[.//span[contains(text(), "Log In")]]')))

#         # # Click the button
#         # login_button.click()

#         # //*[@id="login"]/auth-flow-modal/div[2]/faceplate-tracker/button
#         # Wait for login to complete
#         # WebDriverWait(driver, 10).until(
#         #     EC.presence_of_element_located((By.XPATH, "//a[@href='/submit']"))
#         # )
        
#         # # Add random delay to mimic human behavior
#         time.sleep(random.uniform(2, 4))
        
#         # # # Navigate to subreddit
#         # driver.get(f"https://www.reddit.com/r/{subreddit}/")
        
#         # # # Wait for posts to load
#         # WebDriverWait(driver, 10).until(
#         #     EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='post-container']"))
#         # )
        
#         # # Find post elements
#         # post_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-testid='post-container']")
        
#         # # Iterate through posts
#         # for post in post_elements[:10]:  # Limit to 10 posts
#         #     try:
#         #         # Extract post details
#         #         title = post.find_element(By.CSS_SELECTOR, "h3").text
                
#         #         # Try to get upvotes
#         #         try:
#         #             upvotes = post.find_element(By.CSS_SELECTOR, "div[id^='vote-arrows-']").text
#         #         except:
#         #             upvotes = "N/A"
                
#         #         # Try to get link
#         #         try:
#         #             link = post.find_element(By.CSS_SELECTOR, "a[data-click-id='body']").get_attribute('href')
#         #         except:
#         #             link = "No link available"
                
#         #         posts.append({
#         #             "title": title,
#         #             "upvotes": upvotes,
#         #             "link": link
#         #         })
            
#         #     except Exception as post_error:
#         #         print(f"Error processing individual post: {post_error}")
        
#     except Exception as e:
#         print(f"Login or scraping error: {e}")
#         return [{"error": str(e)}]
    
#     finally:
#         driver.quit()
    
#     return posts

# @app.route('/scrape', methods=['POST'])
# def scrape_reddit():
#     """
#     Flask endpoint for scraping Reddit posts
    
#     Expected JSON payload:
#     {
#         "username": "your_reddit_username",
#         "password": "your_reddit_password",
#         "subreddit": "technology"
#     }
#     """
#     # Get data from request
#     data = request.json
    
#     # Validate input
#     if not all(key in data for key in ['subreddit']):
#         return jsonify({
#             "error": "Missing required parameters. subreddit"
#         }), 400
    
#     try:
#         # Perform scraping
#         results = reddit_login_and_scrape(
#             'Final-Difference7055', 
#             '#CW2968honey', 
#             data['subreddit']
#         )
        
#         # Check for errors
#         if results and 'error' in results[0]:
#             return jsonify({
#                 "error": results[0]['error']
#             }), 500
        
#         return jsonify({
#             "posts": results
#         }), 200
    
#     except Exception as e:
#         return jsonify({
#             "error": str(e)
#         }), 500

# @app.route('/', methods=['GET'])
# def health_check():
#     """Simple health check endpoint"""
#     return jsonify({
#         "status": "healthy",
#         "message": "Reddit Scraper API is running"
#     }), 200

# if __name__ == '__main__':
#     # Use environment variable for port, default to 5000
#     port = int(os.environ.get('PORT', 5000))
#     app.run(host='127.0.0.34', port=port,debug=True)
