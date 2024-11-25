from flask import Flask, jsonify, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)

# CORS Configuration
from flask_cors import CORS
CORS(app)

# Configure Selenium

def get_webpage_title(url: str) -> str:
    try:
        # Configure Chrome options for headless mode
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Start ChromeDriver service
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
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
    Example: /get-title/?url=https://www.google.com
    """
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "URL parameter is required"}), 400
    try:
        title = get_webpage_title(url)
        return jsonify({"url": url, "title": title})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.20", port=7860, debug=True)
