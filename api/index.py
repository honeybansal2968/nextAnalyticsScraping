# from flask import Flask, jsonify, request
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager import ChromeDriverManager
# from selenium.webdriver.chrome.options import Options
# import os

# app = Flask(__name__)

# # CORS Configuration
# from flask_cors import CORS
# CORS(app)

# # Configure Selenium

# def get_webpage_title(url: str) -> str:
#     try:
#         # Configure Chrome options for headless mode
#         chrome_options = Options()
#         chrome_options.add_argument("--headless")
#         chrome_options.add_argument("--no-sandbox")
#         chrome_options.add_argument("--disable-dev-shm-usage")
        
#         # Start ChromeDriver service
#         service = Service(ChromeDriverManager().install())
#         driver = webdriver.Chrome(service=service, options=chrome_options)
        
#         # Open the webpage
#         driver.get(url)
        
#         # Get the title
#         title = driver.title
        
#         # Quit driver
#         driver.quit()
        
#         return title
#     except Exception as e:
#         return str(e)

# @app.route("/", methods=["GET"])
# def home():
#     return jsonify({"message": "Hello"})

# @app.route("/get-title/", methods=["GET"])
# def fetch_title():
#     """
#     Fetch the title of a webpage by URL.
#     Example: /get-title/?url=https://www.google.com
#     """
#     url = request.args.get("url")
#     if not url:
#         return jsonify({"error": "URL parameter is required"}), 400
#     try:
#         title = get_webpage_title(url)
#         return jsonify({"url": url, "title": title})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# # if __name__ == "__main__":
# #     app.run(host="127.0.0.20", port=7860, debug=True)

from flask import Flask, jsonify
import threading
import time
import requests
from flask_cors import CORS
app = Flask(__name__)

# URL to call
website_url = "https://hulkbuster-flask-test.hf.space"
CORS(app, resources={r"/*": {"origins": "*"}})
# To store the last response from the website
website_data = {}



# Function to call the website every 10 seconds
def call_website_periodically():
    global website_data
    while True:
        try:
            # Make a request to the website
            response = requests.get(website_url)
            website_data['status_code'] = response.status_code
            website_data['content'] = response.text
            print(f"Called {website_url}, Status: {response.status_code}")
        except Exception as e:
            website_data['error'] = str(e)
            print(f"Error calling {website_url}: {e}")
        
        # Wait for 10 seconds before calling the website again
        time.sleep(600)

# Start the background thread
def start_background_task():
    thread = threading.Thread(target=call_website_periodically)
    thread.daemon = True  # Daemonize thread to stop with the main program
    thread.start()

@app.route('/')
def home():
    start_background_task()
    return 'Hello, World!'

# API to fetch the latest website data
@app.route('/get_website_data', methods=['GET'])
def get_website_data():
    return jsonify(website_data)

# if __name__ == '__main__':
#     start_background_task()
#     app.run(debug=True)