import os
import stat
from flask import Flask, jsonify, request
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
from fake_headers import Headers
from flask_cors import CORS
from webdriver_manager.core.driver_cache import DriverCacheManager
app = Flask(__name__)
CORS(app)

# Set custom WebDriver cache directory
custom_wdm_cache = os.path.join(os.getcwd(), 'custom_wdm_cache')
os.environ['WDM_LOCAL'] = custom_wdm_cache

# Function to install the driver and set executable permissions
def setup_chromedriver():
    
    # cache_manager=DriverCacheManager(custom_wdm_cache)
    # path=GeckoDriverManager(cache_manager=cache_manager).install()
    # # Ensure the driver is executable
    # os.chmod(path, stat.S_IRWXU)  # chmod +x for the owner
    # print("Driver path:", path)
    return 'custom_wdm_cache/.wdm/drivers/geckodriver/win64/v0.35.0/geckodriver.exe'


# Configure Selenium
def get_webpage_title(url: str) -> str:
    try:
        header = Headers().generate()["User-Agent"]

        # Configure Chrome options for headless mode
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.binary_location = "133.0/firefox.exe"
        # Install the WebDriver and set permissions
        driver_path = setup_chromedriver()
        service = Service(executable_path=driver_path)

        # Initialize the WebDriver
        driver = webdriver.Firefox(service=service, options=chrome_options)

        # Open the webpage
        driver.get(url)

        # Get the title
        title = driver.title

        # Quit driver
        driver.quit()

        return title
    except Exception as e:
        return str(e)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Hello"})

@app.route("/get-title/", methods=["GET"])
def fetch_title():
    """
    Fetch the title of a webpage by URL.
    Example: /get-title/?url=https://www.reddit.com
    """
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "URL parameter is required"}), 400
    try:
        title = get_webpage_title(url)
        return jsonify({"url": url, "title": title})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Uncomment this line to run the app directly
if __name__ == "__main__":
    app.run(host="127.0.0.20", port=7860, debug=True)