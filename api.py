from flask import Flask, request, jsonify
import threading
import asyncio
import time
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from scraper import scrape_news  

app = Flask(__name__)
executor = ThreadPoolExecutor()

def log_api_request(user_id, query, results, inference_time):
    conn = sqlite3.connect('api_requests.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            query TEXT,
            results TEXT,
            inference_time REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        INSERT INTO api_requests (user_id, query, results, inference_time)
        VALUES (?, ?, ?, ?)
    ''', (user_id, query, str(results), inference_time))

    conn.commit()
    conn.close()

def update_user_call_frequency(user_id):
    conn = sqlite3.connect('user_calls.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_calls (
            user_id TEXT PRIMARY KEY,
            call_frequency INTEGER
        )
    ''')

    cursor.execute('SELECT call_frequency FROM user_calls WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    if result:
        new_frequency = result[0] + 1
        cursor.execute('UPDATE user_calls SET call_frequency = ? WHERE user_id = ?', (new_frequency, user_id))
    else:
        new_frequency = 1
        cursor.execute('INSERT INTO user_calls (user_id, call_frequency) VALUES (?, ?)', (user_id, new_frequency))

    conn.commit()
    conn.close()
    
    return new_frequency

def get_from_database(query, top_k):
    conn = sqlite3.connect('articles.db')
    cursor = conn.cursor()
    cursor.execute('PRAGMA table_info(articles)')
    columns = [row[1] for row in cursor.fetchall()]
    if 'query' not in columns:
        cursor.execute('ALTER TABLE articles ADD COLUMN query TEXT')

    cursor.execute('SELECT link FROM articles WHERE query = ?', (query,))
    results = cursor.fetchall()

    conn.close()
    return [{'link': row[0]} for row in results[:top_k]]

def save_to_database(results, query):
    conn = sqlite3.connect('articles.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT,
            link TEXT,
            UNIQUE(query, link)
        )
    ''')
    for result in results:
        cursor.execute('INSERT OR IGNORE INTO articles (query, link) VALUES (?, ?)', (query, result['link']))

    conn.commit()
    conn.close()

async def fetch_articles(text, top_k):
    return await scrape_news(text, top_k)

def run_background_task():
    while True:
        asyncio.run(fetch_articles('legal web scraping', 5))
        time.sleep(3600)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "API is active"}), 200

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    text = data.get('text', '')
    top_k = data.get('top_k', 5)
    threshold = data.get('threshold', 0.8)
    user_id = data.get('user_id', '')

    call_frequency = update_user_call_frequency(user_id)
    if call_frequency > 5:
        return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429

    start_time = time.time()  
    cached_results = get_from_database(text, top_k)
    if cached_results:
        results = cached_results
    else:
        future = executor.submit(asyncio.run, fetch_articles(text, top_k))
        results = future.result()
        save_to_database(results, text)

    end_time = time.time()  
    inference_time = end_time - start_time

    formatted_results = [{'link': result['link'], 'title': result.get('title', 'No title available')} for result in results]

    log_api_request(user_id, text, formatted_results, inference_time)

    return jsonify({
        "query": text,
        "top_k": top_k,
        "threshold": threshold,
        "results": formatted_results,
        "inference_time": inference_time
    }), 200

if __name__ == '__main__':
    print("Starting Flask server...")
    thread = threading.Thread(target=run_background_task)
    thread.daemon = True
    thread.start()
    app.run(debug=True)
