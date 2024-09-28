import re
import os
import json
from dotenv import load_dotenv
from pymongo import MongoClient
import openai 
import pdfplumber
from PIL import Image
import io
from langchain_community.document_loaders import PDFPlumberLoader

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def clean_text(text):
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    return text

def extract_text_from_pdf(filename):
    # Open PDF and extract text
    full_paper = ""

    with pdfplumber.open(filename) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_paper += clean_text(text) + " "
    
    return full_paper


def generate_code_from_description(description):
    prompt = f"Generate Python code for the following methodology, look through all the steps taken and generate code that precisely mimics them.:\n\n{description}"
    

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates Python code based on provided methodologies."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000
    )

    
    return response.choices[0].message.content

def code_generation(text):
    # full_paper = extract_text_from_pdf(filename=filename)
    response = generate_code_from_description(text)

    return response