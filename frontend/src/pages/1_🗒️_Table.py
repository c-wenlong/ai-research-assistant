import time
import streamlit as st
import json
import pandas as pd
import os
from st_aggrid import AgGrid, GridOptionsBuilder
import pymongo
import re
import ast
from dotenv import load_dotenv

load_dotenv()


def fetch_data_from_mongodb_pdf():
    client = pymongo.MongoClient(os.getenv("MONGODB_URL"))

    db = client["research_articles"]
    collection = db["pdf_upload_papers"]

    # Retrieve all documents from the collection
    papers = collection.find()
    return papers, client


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


# Main function
def load_database_pdf():
    papers, client = fetch_data_from_mongodb_pdf()

    # Process all files
    all_data = []
    for data in papers:
        display_data = {
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
            "References": truncate_text(
                format_reference(data.get("references", [])), max_words=100
            ),
        }
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


# Main application function
def main():
    st.title("Knowledge Base")
    data = load_database_pdf()
    load_table(data, "pdf")


main()
