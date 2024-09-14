import requests
from bs4 import BeautifulSoup
import sqlite3
import time

DATABASE = 'news_articles.db'

def init_db():
    "SQLite is init"
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                url TEXT,
                content TEXT
            )
        ''')
        conn.commit()

def insert_article(title, url, content):
    "article added to db"
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO articles (title, url, content) VALUES (?, ?, ?)
        ''', (title, url, content))
        conn.commit()

def scrape_news():
    "scraping google news"
    print("Google news scrape started")
    url = 'https://news.google.com'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('article')
    for article in articles:
        title = article.find('h3').text if article.find('h3') else 'No Title'
        link = article.find('a')['href'] if article.find('a') else 'No URL'
        content = 'No Content'  
            
        if not link.startswith('http'):
            link = 'https://news.google.com' + link

        insert_article(title, link, content)
        
    print("Scraping complete.")



def background_task():
    "bg scrape __________________ "
    init_db()  
    while True:
        scrape_news()
        time.sleep(3600)  
