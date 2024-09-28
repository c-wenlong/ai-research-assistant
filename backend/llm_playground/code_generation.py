import re
import os
import json
from dotenv import load_dotenv
import openai 
import pdfplumber
from langchain_community.document_loaders import PDFPlumberLoader
import anthropic

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
# client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
    
    message = client.messages.create(
    model="claude-3-5-sonnet-20240620",
    max_tokens=800,
    temperature=0,
    system="You are a world-class poet. Respond only with short poems.",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                }
                ]
            }
        ]
    )
    return(message.content[0].text)

    # response = client.chat.completions.create(
    #     model="gpt-4o-mini",
    #     messages=[
    #         {"role": "system", "content": "You are a helpful assistant that generates Python code based on provided methodologies. Optimise your response time and keep the response to 750 tokens"},
    #         {"role": "user", "content": prompt}
    #     ],
    #     max_tokens=800,
    #     temperature=0
    #     # stream=True
    # )
    # # result = ""
    # # for chunk in response:
    # #     # print(chunk.choices[0].delta.content)
    # #     if chunk.choices[0].delta.content:
    # #         result += chunk.choices[0].delta.content

    # # return result

    # return response.choices[0].message.content

def code_generation(text):
    # full_paper = extract_text_from_pdf(filename=filename)
    response = generate_code_from_description(text)

    return response