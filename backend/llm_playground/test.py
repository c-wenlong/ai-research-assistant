import rag_function as rf
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()
print(f"MONGO_URI: {os.getenv('MONGO_URI')}")
print(f"MONGO_DB_NAME: {os.getenv('MONGO_DB_NAME')}")
print(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')}")

mongo_uri = os.getenv("MONGO_URI")
db_name = os.getenv("MONGO_DB_NAME")
collection_name = 'gut_microbiome'
llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini-2024-07-18")

# rf.create_knowledge_graph(mongo_uri=mongo_uri, db_name=db_name, collection_name=collection_name, llm=llm)

response = rf.llm_output("what is good about microbatacn?")
print(response)