import sqlite3
from GoogleNews import GoogleNews
from requests_html import HTMLSession

googlenews = GoogleNews(lang='en')

async def scrape_news(query, top_k):
    googlenews = GoogleNews(lang='en')
    googlenews.search(query)
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
            
            store_articles(newsarticle)
        except Exception as e:
            print(f"Error extracting article: {e}")

    return newslist

def store_articles(article):
    
    conn = sqlite3.connect('articles.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            link TEXT
        )
    ''')

    cursor.execute('''
        INSERT INTO articles (title, link)
        VALUES (?, ?)
    ''', (article['title'], article['link']))

    conn.commit()
    conn.close()
