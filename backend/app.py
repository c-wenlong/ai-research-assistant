from flask import Flask, Response, jsonify, request
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import asyncio
from web_scrape.scrape_optimized import main  # Ensure this imports your async main function
from llm_playground import rag_function as rf
from llm_playground import code_generation as cg
from langchain_openai import ChatOpenAI
import threading
import time
import json
from flask_caching import Cache
from threading import Thread

load_dotenv()

app = Flask(__name__)
cache = Cache(config={'CACHE_TYPE': 'simple'})
cache.init_app(app)
llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini-2024-07-18")

# Connect to MongoDB
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client['research_articles']
summarized_collection = db['summarized_fields_article']
raw_collection = db['raw_fields_article']

gap_individual_articles_collection = db['gap_individual_articles']
gap_comparison_section_collection = db['gap_comparison_section']

@app.route('/articles-summarized', methods=['GET'])
def get_articles_summarized():
    try:
        articles = list(summarized_collection.find())
        for article in articles:
            article['_id'] = str(article['_id'])  # Convert ObjectId to string
        return jsonify(articles), 200
    except Exception as e:
        print(f"Error fetching summarized articles: {e}")
        return jsonify({"error": "Failed to fetch summarized articles"}), 500

@app.route('/api/get_response', methods=['POST'])
def get_response():
    data = request.json
    user_input = data.get("user_input")
    
    response = rf.llm_output(user_input) 
    
    return jsonify({"response": response})

@app.route('/api/generate_code', methods=['POST'])
@cache.cached(timeout=120, query_string=True)
def produce_code():
    data = request.json
    user_input = data.get("user_input")
    
    response = cg.code_generation(user_input)
    
    return jsonify({"response": response})

@app.route('/web_search', methods=['POST'])
def search_articles():
    user_input = request.json.get('query')
    if not user_input:
        return jsonify({"error": "No query provided"}), 400
    try:
        summarized_collection.delete_many({})
        raw_collection.delete_many({})
        gap_individual_articles_collection.delete_many({})
        gap_comparison_section_collection.delete_many({})
    except Exception as e:
        print(f"Error clearing collections: {e}")
        return jsonify({"error": "Failed to clear collections", "details": str(e)}), 500
    
    print(f"Received query: {user_input}")

    # Define a function to wrap the asyncio.run() call in a thread
    def run_async_main():
        asyncio.run(main(user_input))

    # Start the thread to run the async function
    thread = Thread(target=run_async_main)
    thread.start()
    thread.join()

    return jsonify({"message": "Search completed successfully."}), 200

    # # Run the async main function using asyncio.run()
    # asyncio.run(main(user_input))
    # # threading.Thread(target=rf.create_knowledge_graph, args=(mongo_uri, 'research_articles', 'raw_fields_article', llm)).start()
    # return jsonify({"message": "Search completed successfully."}), 200

if __name__ == "__main__":
    app.run(debug=True)