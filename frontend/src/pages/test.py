import pymongo


def fetch_data_from_mongodb():
    client = pymongo.MongoClient("mongodb+srv://wenlongc:wl123@knowledge.c44yv.mongodb.net/?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true")
    db = client["research_articles"]
    collection = db["gut_microbiome"]

    # Retrieve all documents from the collection
    papers = collection.find()
    # Process each paper into a Document for the graph
    for json_data in papers:
        print(json_data.get("title"))
    client.close()


if __name__ == "__main__":
    fetch_data_from_mongodb()
