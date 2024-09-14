from playwright.async_api import async_playwright
import asyncio
import threading

async def scrape_news():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://news.google.com/topstories?hl=en-GB&gl=GB&ceid=GB:en')

        for _ in range(5):
            await page.evaluate('window.scrollBy(0, window.innerHeight)')
            await page.wait_for_timeout(1000)

        articles = await page.query_selector_all('article')
        newslist = []

        for item in articles:
            try:
                newsitem = await item.query_selector('h3')
                title = await newsitem.inner_text()
                link = await newsitem.get_attribute('href')
                newsarticle = {
                    'title': title,
                    'link': link
                }
                newslist.append(newsarticle)
            except Exception as e:
                print(f"Error extracting article: {e}")

        await browser.close()
        print(f"Scraped {len(newslist)} articles")
        return newslist  

def background_task():
    asyncio.run(run_background_task())

async def run_background_task():
    while True:
        await scrape_news()
        await asyncio.sleep(3600) 

if __name__ == "__main__":
    thread = threading.Thread(target=background_task)
    thread.start()
