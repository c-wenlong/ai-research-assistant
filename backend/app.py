from flask import Flask, jsonify, request
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import asyncio
from web_scrape.scrape_optimized import main  # Ensure this imports your async main function
from llm_playground import rag_function as rf
from langchain_openai import ChatOpenAI

load_dotenv()

app = Flask(__name__)

# Connect to MongoDB
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client['research_articles']
summarized_collection = db['summarized_fields_article']
raw_collection = db['raw_fields_article']

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
    
@app.route('/search', methods=['POST'])
def search_articles():
    user_input = request.json.get('query', '')
    if not user_input:
        return jsonify({"error": "No query provided"}), 400

    # Clear the documents in the collections before running main
    try:
        summarized_collection.delete_many({})  # Clear summarized articles
        raw_collection.delete_many({})  # Clear raw articles
    except Exception as e:
        print(f"Error clearing collections: {e}")
        return jsonify({"error": "Failed to clear collections", "details": str(e)}), 500

    # Run the async main function using asyncio.run()
    try:
        results = asyncio.run(main(user_input))
        return jsonify(results), 200
    except Exception as e:
        print(f"Error during search: {e}")  # Print the specific error message
        return jsonify({"error": "Search failed", "details": str(e)}), 500  # Include error details in the response

if __name__ == "__main__":
    app.run(debug=True)