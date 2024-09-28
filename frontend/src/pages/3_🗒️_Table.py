import streamlit as st
import json
import pandas as pd
import os
from st_aggrid import AgGrid, GridOptionsBuilder
from PyPDF2 import PdfReader
import requests

# Set the page configuration
st.set_page_config(layout="wide", page_title="Your Papers", page_icon="📚")

ARTICLES_SUMMARIZED_URL = "http://127.0.0.1:5000/articles-summarized"

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
    assets_dir = os.path.join(script_dir, directory)

    for filename in os.listdir(assets_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(assets_dir, filename)
            with open(file_path, "r") as file:
                json_files[filename] = json.load(file)
    return json_files

# Function to load JSON articles
def load_json():
    json_files = load_json_files(st.secrets["PDF_PATH"])
    all_data = []
    for filename, data in json_files.items():
        display_data = {
            "PMC ID": data.get("pmc_id", "N/A"),
            "Title": data.get("title", "N/A"),
            "Abstract": truncate_text(data.get("abstract", "N/A")),
            "Authors": create_multiselect(data.get("authors", [])),
            "Publication Date": data.get("publication_date", "N/A"),
            "Journal Name": data.get("journal_name", "N/A"),
            "DOI": data.get("doi", "N/A"),
            "Keywords": create_multiselect(data.get("keywords", [])),
            "Introduction": truncate_text(data.get("Introduction", "N/A")),
            "Methods": truncate_text(data.get("Methods", "N/A")),
            "Results": truncate_text(data.get("Results", "N/A")),
            "Discussion": truncate_text(data.get("Discussion", "N/A")),
            "Conclusion": truncate_text(data.get("Conclusion", "N/A")),
            "References": create_multiselect(data.get("References", [])),
        }
        all_data.append(display_data)
    return all_data

# Function to load uploaded PDFs
def load_uploaded_pdfs(uploaded_files):
    all_data = []
    for uploaded_file in uploaded_files:
        pdf_reader = PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + " "

        display_data = {
            "PMC ID": "N/A",
            "Title": uploaded_file.name,
            "Abstract": truncate_text(text, max_words=50),
            "Authors": "N/A",
            "Publication Date": "N/A",
            "Journal Name": "N/A",
            "DOI": "N/A",
            "Keywords": "N/A",
            "Introduction": "N/A",
            "Methods": "N/A",
            "Results": "N/A",
            "Discussion": "N/A",
            "Conclusion": "N/A",
            "References": "N/A",
        }
        all_data.append(display_data)
    return all_data

# Function to load and display data in an AgGrid table
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

    # Load and display the JSON papers
    if 'results' in st.session_state:
        # Fetch summarized articles from the backend if results exist
        response = requests.get(ARTICLES_SUMMARIZED_URL)

        if response.status_code == 200:
            summarized_articles = response.json()
            st.subheader("Summarized Articles")
            if summarized_articles:
                load_table(summarized_articles)
            else:
                st.warning("No summarized articles found.")
        else:
            st.error("Error retrieving summarized articles")
    else:
        st.warning("No search results available. Please perform a search first.")

    # Upload PDF files
    st.subheader("Your Uploaded Papers")
    uploaded_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)

    if uploaded_files:
        all_data_uploaded = load_uploaded_pdfs(uploaded_files)
        load_table(all_data_uploaded)

main()