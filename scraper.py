import sqlite3
from GoogleNews import GoogleNews
from requests_html import HTMLSession
import asyncio

googlenews = GoogleNews(lang='en')

def create_database():
    conn = sqlite3.connect('articles.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            link TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def insert_article(title, link):
    conn = sqlite3.connect('articles.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO articles (title, link)
        VALUES (?, ?)
    ''', (title, link))
    conn.commit()
    conn.close()

async def scrape_news():
    googlenews.search('legal web scraping')
    results = googlenews.result()

    newslist = []
    for item in results:
        try:
            title = item['title']    
            link = item['link']      
            newsarticle = {
                'title': title,
                'link': link
            }
            newslist.append(newsarticle)
            insert_article(title, link)
        
        except Exception as e:
            print(f"Error extracting article: {e}")

    print(f"News scraped: {len(newslist)} articles")

async def background_task():
    create_database()  
    while True:
        await scrape_news()
        await asyncio.sleep(3600)  

def run_background_task():
    asyncio.run(background_task())
