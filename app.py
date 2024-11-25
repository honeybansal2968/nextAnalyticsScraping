from fastapi import FastAPI, HTTPException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference
from scalar_fastapi.scalar_fastapi import Layout

app = FastAPI()

app = FastAPI(
    debug=True,
    title="NextAnalytics Server",
    consumes=["application/x-www-form-urlencoded", "multipart/form-data"],
    docs_url='/swagger'
)
# CORS configuration
origins = [
    "*",
    # Add more origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specified origins
    allow_credentials=False,
    allow_methods=["*"],     # Allows all HTTP methods
    allow_headers=["*"],     # Allows all headers
)

# Configure Selenium
CHROMEDRIVER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chromedriver.exe")
@app.get("/docs", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
        layout=Layout.CLASSIC,
        servers= [
            {
                'url': os.getenv('BASE_URL') or f"http://127.0.0.23:7860",
            },
        ]
    )
def get_webpage_title(url: str) -> str:
    try:
        # Configure Chrome options for headless mode
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Start ChromeDriver service
        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Open the webpage
        driver.get(url)

        # Get the title
        title = driver.title

        # Quit driver
        driver.quit()

        return title
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read():
    return {"url":"hello"}

# FastAPI Endpoint
@app.get("/get-title/")
async def fetch_title(url: str):
    """
    Fetch the title of a webpage by URL.
    Example: /get-title/?url=https://www.google.com
    """
    return {"url": url, "title": get_webpage_title(url)}
