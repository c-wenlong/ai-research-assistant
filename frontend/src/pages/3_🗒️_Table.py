from PyPDF2 import PdfReader
import streamlit as st
import json
import pandas as pd
import os
from st_aggrid import AgGrid, GridOptionsBuilder
import pymongo

# Set the page configuration
st.set_page_config(layout="wide", page_title="Your Papers", page_icon="📚"),


def fetch_data_from_mongodb_pubmed():
    client = pymongo.MongoClient(st.secrets["MONGODB_URL"])

    db = client["research_articles"]
    collection = db["gut_microbiome"]

    # Retrieve all documents from the collection
    papers = collection.find()
    return papers, client


def fetch_data_from_mongodb_pdf():
    client = pymongo.MongoClient(st.secrets["MONGODB_URL"])

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
def create_multiselect(options: list) -> str:
    if not options or len(options) == 1:
        return "N/A"
    return " | ".join(str(option) for option in options)

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


def create_multiselect(options: list) -> str:
    if not options or len(options) == 1:
        return "N/A"

    return " | ".join(str(option) for option in options)


# Main functions
def load_database_pubmed():
    papers, client = fetch_data_from_mongodb_pubmed()

    # Process all files
    all_data = []
    for data in papers:
        display_data = {
            "PMC ID": data.get("pmc_id", "N/A"),
            "Title": data.get("title", "N/A"),
            "Abstract": truncate_text(data.get("abstract", "N/A")),
            "Authors": create_multiselect(data.get("authors", [])),
            "Publication Date": data.get("publication_date", "N/A"),
            "Journal Name": data.get("journal_name", "N/A"),
            "DOI": data.get("doi", "N/A"),
            "Keywords": create_multiselect(data.get("keywords", [])),
            "Introduction": truncate_text(data.get("introduction", "N/A")),
            "Methods": truncate_text(data.get("methods", "N/A")),
            "Results": truncate_text(data.get("results", "N/A")),
            "Discussion": truncate_text(data.get("discussion", "N/A")),
            "Conclusion": truncate_text(data.get("conclusion", "N/A")),
            "References": create_multiselect(data.get("references", [])),
        }
        all_data.append(display_data)

    client.close()
    return all_data


def load_database_pdf():
    papers, client = fetch_data_from_mongodb_pubmed()

    # Process all files
    all_data = []
    for data in papers:
        display_data = {
            "Title": data.get("title", "N/A"),
            "Abstract": truncate_text(data.get("abstract", "N/A")),
            "Authors": create_multiselect(data.get("authors", [])),
            "Publication Date": data.get("publication_date", "N/A"),
            "Journal Name": data.get("journal_name", "N/A"),
            "DOI": data.get("doi", "N/A"),
            "Keywords": create_multiselect(data.get("keywords", [])),
            "Introduction": truncate_text(data.get("introduction", "N/A")),
            "Methods": truncate_text(data.get("methods", "N/A")),
            "Results": truncate_text(data.get("results", "N/A")),
            "Discussion": truncate_text(data.get("discussion", "N/A")),
            "Conclusion": truncate_text(data.get("conclusion", "N/A")),
            "References": create_multiselect(data.get("references", [])),
        }
        all_data.append(display_data)

    client.close()
    return all_data


def load_table(all_data):
    display_df = pd.DataFrame(all_data)
    gb = GridOptionsBuilder.from_dataframe(display_df)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar(filters_panel=True, columns_panel=True)
    gb.configure_default_column(wrapText=True, autoHeight=True, maxWidth=500, groupable=True)
    gb.configure_grid_options(enableRangeSelection=True)

    gridOptions = gb.build()
    AgGrid(display_df, gridOptions=gridOptions, fit_columns_on_grid_load=False, enable_enterprise_modules=True, height=500, theme="streamlit")

# Main application function
def main():
    st.title("Your Papers")
    all_data = load_database_pubmed()
    load_table(all_data)
    data = load_database_pdf()
    load_table(data)


main()