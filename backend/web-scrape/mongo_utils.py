from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

def save_to_mongodb(articles, collection_name):
    """Insert multiple articles into MongoDB."""
    try:
        mongo_uri = os.getenv("MONGO_URI")
        client = MongoClient(mongo_uri)
        client.admin.command('ping')
        print("Connection successful!")
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    db = client['research_articles']  # Use 'research_articles' database
    collection = db[collection_name]  # Use 'gut_microbiome' collection

    # Insert multiple documents into the collection
    result = collection.insert_many(articles)
    print(f"Inserted {len(result.inserted_ids)} documents with ids: {result.inserted_ids}")