import pymongo
import streamlit as st

# Define the MongoDB references
mongoUrl = st.secrets["MONGODB_URL"]
db = "research_articles"
collection = "gut_microbiome"

# Replace the following with your actual connection string
client = pymongo.MongoClient(mongoUrl)

# Access the database and collection
db = client[db]  # Replace with your actual database name
collection = db[collection]  # Replace with your actual collection name

# Fetch all documents from the collection
documents = collection.find()

# Process and print the documents
for doc in documents:
    print(doc)

client.close()

'''
def main():
    pass


if __name__ == "__main__":
    main()
'''