import time
from selenium_driverless import webdriver
import asyncio


async def main():
    options = webdriver.ChromeOptions()
    async with webdriver.Chrome(options=options) as driver:
        await driver.get('https://www.reddit.com')
        time.sleep(3)

        title = await driver.title
        url = await driver.current_url
        source = await driver.page_source
        print(title)


asyncio.run(main())