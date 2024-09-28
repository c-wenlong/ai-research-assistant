import ast
import re
import streamlit as st
import requests
import json
import time
from dotenv import load_dotenv
import pymongo
from openai import OpenAI
import os
from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd

load_dotenv()


def fetch_data_from_mongodb_pubmed():
    client = pymongo.MongoClient(os.getenv("MONGODB_URL"))

    db = client["research_articles"]
    collection = db["summarized_fields_article"]

    # Retrieve all documents from the collection
    papers = collection.find()
    return papers, client


# Function to generate keywords
def generate_keywords(prompt, text):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    try:
        # Call the OpenAI API with GPT-4
        userPrompt = (
            "Below is the JSON summary of a paper, generate keywords for the paper, and only output the keywords. In the format ['keyword 1', 'keyword 2', 'keyword 3']: "
            + text
        )
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Specify GPT-4 model
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": userPrompt},
            ],
        )

        # Extract and return the response text
        return response.choices[0].message.content

    except Exception as e:
        print(f"Error occurred: {e}")
        return None


# Function to truncate text
def truncate_text(text, max_words=50):
    if text is None or text == "":
        return "N/A"
    words = text.split()
    if len(words) > max_words:
        return " ".join(words[:max_words]) + "..."
    return text


# Function to create a multiselect string from a list
def format_list(options: list) -> str:
    if not options or len(options) == 1:
        return "N/A"
    return " | ".join(str(option) for option in options)


# Function to format references
def format_reference(options: list) -> str:
    if not options or len(options) == 1:
        return "N/A"

    formatted_references = []
    index = 1
    for option in options:
        if isinstance(option, dict):
            authors = option.get("authors", "N/A")
            title = option.get("title", "N/A")
            journal = option.get("journal_name", "N/A")
            year = option.get("publication_date", "N/A").split()[-1]  # Extract year

            reference = f"{index}. {authors} ({year}). {title}. {journal}. \n"
            formatted_references.append(reference)
            index += 1

    return "\n".join(formatted_references)


# Function to load JSON files from a directory
def load_json_files(directory):
    json_files = {}
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # print("Script directory:", script_dir)
    assets_dir = os.path.join(script_dir, directory)
    # print("Assets directory:", assets_dir)

    for filename in os.listdir(assets_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(
                assets_dir, filename
            )  # Use assets_dir here, not directory
            # print(f"Loading file: {file_path}")
            with open(file_path, "r") as file:
                json_files[filename] = json.load(file)
    return json_files


# Function to process the markdown file
def process_md(file_path):
    with open(file_path, "r") as file:
        return file.read()


def process_keywords_output(llm_output):
    # Remove any leading/trailing whitespace
    cleaned_output = llm_output.strip()

    # Check if the output is already in the correct format
    if cleaned_output.startswith("[") and cleaned_output.endswith("]"):
        try:
            # Try to parse the string as a literal Python list
            keywords = ast.literal_eval(cleaned_output)
            return keywords
        except (SyntaxError, ValueError):
            # If parsing fails, fall back to regex method
            pass

    # If not in the correct format, use regex to extract keywords
    keyword_pattern = r"['\"](.*?)['\"]"
    keywords = re.findall(keyword_pattern, cleaned_output)

    # Remove any empty strings and strip whitespace
    keywords = [keyword.strip() for keyword in keywords if keyword.strip()]

    return keywords


# Main functions
def load_database_pubmed():
    papers, client = fetch_data_from_mongodb_pubmed()
    prompt = process_md("./frontend/src/assets/keyword-generation-prompt.md")
    # Process all files
    all_data = []
    for data in papers:
        display_data = {
            "PMC ID": data.get("pmc_id", "N/A"),
            "Title": data.get("title", "N/A"),
            "Abstract": truncate_text(data.get("abstract", "N/A")),
            "Authors": format_list(data.get("authors", [])),
            "Publication Date": data.get("publication_date", "N/A"),
            "Journal Name": data.get("journal_name", "N/A"),
            "DOI": data.get("doi", "N/A"),
            "Keywords": format_list(data.get("keywords", [])),
            "Introduction": truncate_text(data.get("introduction", "N/A")),
            "Methods": truncate_text(data.get("methods", "N/A")),
            "Results": truncate_text(data.get("results", "N/A")),
            "Discussion": truncate_text(data.get("discussion", "N/A")),
            "Conclusion": truncate_text(data.get("conclusion", "N/A")),
            # "References": truncate_text(format_list(data.get("references", []))),
        }
        # print(display_data)
        keywords = generate_keywords(prompt, str(display_data))
        processed_keywords = process_keywords_output(keywords)
        display_data["Keywords"] = format_list(processed_keywords)

        all_data.append(display_data)

    client.close()
    return all_data


def load_table(all_data, type):
    display_df = pd.DataFrame(all_data)
    gb = GridOptionsBuilder.from_dataframe(display_df)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar(filters_panel=True, columns_panel=True)
    gb.configure_default_column(
        wrapText=True,
        autoHeight=True,
        maxWidth=500,
        groupable=True,
        cellStyle={"white-space": "pre-wrap"},
    )
    if type == "pdf":
        gb.configure_column(
            "References",
            maxWidth=1000,  # Increase the maximum width for References
            minWidth=500,
        )  # Set a minimum width to ensure it's wider
    gridOptions = gb.build()
    AgGrid(
        display_df,
        gridOptions=gridOptions,
        fit_columns_on_grid_load=False,
        enable_enterprise_modules=True,
        height=500,
        theme="streamlit",
    )


# Function to get current trends and insights
def get_current_trends_and_insights(papers):
    pass


# Define the backend endpoint (replace with your actual endpoint URL)
BACKEND_URL = "http://127.0.0.1:5000/web_search"

# Streamlit configuration for minimalistic appearance
st.set_page_config(page_title="Search App", layout="centered")

# Minimalistic search bar UI
st.title("Search")
search_query = st.text_input("Enter your search query", "")

# Search button to trigger the API request
if st.button("Search"):
    if search_query:
        with st.spinner("Loading... Please wait."):
            try:
                # Sending request to the backend API
                print(f"Sending query: {search_query}")
                response = requests.post(
                    BACKEND_URL, json={"query": search_query}, stream=True
                )

                # Check for the response status
                if response.status_code == 200:
                    st.success("Search completed successfully.")

                    # Reading the streamed response
                    for chunk in response.iter_lines():
                        if chunk:
                            # Decode the chunk and process it as per backend response structure
                            result = json.loads(chunk.decode("utf-8"))
                            st.write(result)
                            time.sleep(1)  # Simulate delay between chunks

                else:
                    st.error(f"Error: {response.status_code} - {response.text}")

            except requests.exceptions.RequestException as e:
                st.error(f"Error while contacting backend: {str(e)}")

    else:
        st.warning("Please enter a search query")


def main():
    message_placeholder = st.empty()
    message_placeholder.success("Fetching articles and summarizing them...")
    st.title("Brainstorming")
    all_data = load_database_pubmed()
    message_placeholder.success("Fetch successful!")
    load_table(all_data, "pubmed")
    time.sleep(3)
    message_placeholder.empty()

    # Create current trends and insights
    st.title("Current Trends and Insights")
    get_current_trends_and_insights(all_data)


main()
