from flask import Flask, request, jsonify
import threading
import asyncio
import sqlite3
import time
from scraper import scrape_news  
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
executor = ThreadPoolExecutor()


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
        
        call_frequency = result[0] + 1
        if call_frequency > 5:
            conn.close()
            return False  
        cursor.execute('UPDATE user_calls SET call_frequency = ? WHERE user_id = ?', (call_frequency, user_id))
    else:
        
        cursor.execute('INSERT INTO user_calls (user_id, call_frequency) VALUES (?, 1)', (user_id,))

    conn.commit()
    conn.close()
    return True  

def run_background_task():
    while True:
        asyncio.run(scrape_news('legal web scraping', 5))
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

    
    if not update_user_call_frequency(user_id):
        return jsonify({"error": "Rate limit exceeded"}), 429

    
    def fetch_articles():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(scrape_news(text, top_k))
        print(f"Results returned: {len(results)}") 
        return results
        
    future = executor.submit(fetch_articles)
    results = future.result()

    return jsonify({
        "query": text,
        "top_k": top_k,
        "threshold": threshold,
        "results": results
    }), 200

if __name__ == '__main__':
    print("Starting Flask server...")
    thread = threading.Thread(target=run_background_task)
    thread.daemon = True
    thread.start()
    app.run(debug=True)
