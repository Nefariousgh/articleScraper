from flask import Flask, request, jsonify
import threading
from scraper import run_background_task
from retriever import search_articles  

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "API is active"}), 200

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    text = data.get('text', '')
    top_k = data.get('top_k', 5)
    threshold = data.get('threshold', 0.8)

    results = search_articles(text, top_k)

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
