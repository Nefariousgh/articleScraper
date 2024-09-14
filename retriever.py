import sqlite3

DATABASE = 'news_articles.db'

def search_articles(query, top_k):
    "atricle search from sqldb "
    results = []
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT title, url FROM articles
            WHERE content LIKE ?
            LIMIT ?
        ''', ('%' + query + '%', top_k))
        rows = cursor.fetchall()
        results = [{"title": row[0], "url": row[1]} for row in rows]

    return results
