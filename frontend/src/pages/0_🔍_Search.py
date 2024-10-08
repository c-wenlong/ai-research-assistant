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
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import pandas as pd

load_dotenv()

# Streamlit configuration for minimalistic appearance
st.set_page_config(page_title="Search App", layout="centered")


def fetch_data_from_mongodb_pubmed():
    client = pymongo.MongoClient(os.getenv("MONGODB_URI"))

    db = client["research_articles"]
    collection = db["summarized_fields_article"]

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


# Convert JSON data to text
def json_to_text(papers):
    processed_papers = []

    for i, paper in enumerate(papers, 1):
        paper_str = f"Paper {i}:\n"
        paper_str += f"PMC ID: {paper.get('PMC ID', 'N/A')}\n"
        paper_str += f"Title: {paper.get('Title', 'N/A')}\n"
        paper_str += f"Abstract: {paper.get('Abstract', 'N/A')}\n"
        paper_str += f"Authors: {paper.get('Authors', 'N/A')}\n"
        paper_str += f"Publication Date: {paper.get('Publication Date', 'N/A')}\n"
        paper_str += f"Journal: {paper.get('Journal Name', 'N/A')}\n"
        paper_str += f"DOI: {paper.get('DOI', 'N/A')}\n"
        paper_str += f"Keywords: {paper.get('Keywords', 'N/A')}\n"

        # Add truncated sections
        sections = ["Introduction", "Methods", "Results", "Discussion", "Conclusion"]
        for section in sections:
            content = paper.get(section, "N/A")
            paper_str += f"{section}: {content}\n"

        paper_str += "\n"

        processed_papers.append(paper_str)

    return "\n".join(processed_papers)


# Main functions
def load_database_pubmed():
    papers, client = fetch_data_from_mongodb_pubmed()
    prompt = process_md("./frontend/src/assets/keyword-generation-prompt.md")
    # Process all files
    all_data = []
    for data in papers:
        display_data = {
            "Link": data.get("article_url", "N/A"),
            "PMC ID": data.get("pmc_id", "N/A"),
            "Title": data.get("title", "N/A"),
            "Abstract": truncate_text(data.get("abstract", "N/A")),
            "Authors": format_list(data.get("authors", [])),
            "Publication Date": data.get("publication_date", "N/A"),
            "Journal Name": data.get("journal_name", "N/A"),
            "DOI": data.get("doi", "N/A"),
            "Introduction": truncate_text(data.get("introduction", "N/A")),
            "Methods": truncate_text(data.get("methods", "N/A")),
            "Results": truncate_text(data.get("results", "N/A")),
            "Discussion": truncate_text(data.get("discussion", "N/A")),
            "Conclusion": truncate_text(data.get("conclusion", "N/A")),
        }

        all_data.append(display_data)

    client.close()
    return all_data

def load_table(all_data):
    display_df = pd.DataFrame(all_data)
    gb = GridOptionsBuilder.from_dataframe(display_df)
    
    # Ensure columns are sortable
    gb.configure_default_column(
        wrapText=True,
        autoHeight=True,
        maxWidth=500,
        groupable=True,
        cellStyle={"white-space": "pre-wrap"},
        sortable=True  # Make columns sortable
    )
    
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar(filters_panel=True, columns_panel=True)
    
    gridOptions = gb.build()
    
    AgGrid(
        display_df,
        gridOptions=gridOptions,
        fit_columns_on_grid_load=False,
        enable_enterprise_modules=True,
        height=500,
        theme="streamlit",
        key="ag_grid_" + str(time.time()),
    )


# Function to fetch individual articles gaps from MongoDB
def fetch_individual_articles_gaps():
    client = pymongo.MongoClient(os.getenv("MONGODB_URI"))
    db = client["research_articles"]
    collection = db["gap_individual_articles"]

    # Retrieve all documents from the collection
    gaps = list(collection.find())
    client.close()
    return gaps

# Function to fetch papers comparison gaps from MongoDB
def fetch_papers_comparison_gaps():
    client = pymongo.MongoClient(os.getenv("MONGODB_URI"))
    db = client["research_articles"]
    collection = db["gap_comparison_section"]

    # Retrieve all documents from the collection
    gaps = list(collection.find())
    client.close()
    return gaps

# Optional: Add a title before the table
st.title("🔍 Search")

# Define the backend endpoint (replace with your actual endpoint URL)
BACKEND_URL = "http://127.0.0.1:5000/web_search"

# Minimalistic search bar UI
search_query = st.text_input("Enter your search query", "")


def main():
    message_placeholder = st.empty()
    message_placeholder.success("Fetching articles and summarizing them...")
    st.subheader("Top Research Articles by Recency")
    all_data = load_database_pubmed()
    message_placeholder.success("Fetch successful!")
    load_table(all_data)
    message_placeholder.empty()

    st.markdown("---")

    # Papers comparison gap analysis
    st.subheader("Papers Comparison Gap Analysis")
    print()
    comparison_gaps = fetch_papers_comparison_gaps()

    if comparison_gaps:
        # Loop through each gap and display it in a more narrative format
        for index, gap in enumerate(comparison_gaps):
            # Extracting lists for each category
            commonalities = gap.get('commonalities', [])
            contrasts = gap.get('contrasts', [])
            emerging_trends = gap.get('emerging_trends', [])

            st.markdown("###### Commonalities")
            if commonalities:
                for commonality in commonalities:
                    st.write(f"- {commonality}")
            else:
                st.write("No commonalities found.")

            st.markdown("###### Contrasts")
            if contrasts:
                for contrast in contrasts:
                    st.write(f"- {contrast}")
            else:
                st.write("No contrasts found.")

            st.markdown("###### Emerging Trends")
            if emerging_trends:
                for trend in emerging_trends:
                    st.write(f"- {trend}")
            else:
                st.write("No emerging trends found.")

            st.markdown("---")  # Add a horizontal line for separation between gaps
    else:
        st.warning("No gaps found for paper comparisons.")

    # Individual paper gap analysis
    st.subheader("Individual Paper Gap Analysis")
    individual_gaps = fetch_individual_articles_gaps()
    if individual_gaps:
        # Create a DataFrame from the individual gaps data
        display_df_individual = pd.DataFrame(individual_gaps)
        
        # Normalize the gap_categories column to create separate columns for each gap type
        gap_df = display_df_individual['gap_categories'].apply(pd.Series)

        # Combine the original DataFrame with the new gap categories DataFrame
        display_data = pd.concat([display_df_individual[['article_title', 'recommendations']], gap_df], axis=1)

        # Optionally, you may want to fill NaN values with empty lists or a default value
        display_data = display_data.fillna("")

        load_table(display_data)
    else:
        st.warning("No gaps found for individual papers.")

# Search button to trigger the API request
if st.button("Search"):
    if search_query:
        with st.spinner("Loading... Please wait."):
            try:
                # Sending request to the backend API
                print(f"Sending query: {search_query}")
                response = requests.post(
                    BACKEND_URL, json={"query": search_query}
                )

                # Check for the response status
                if response.status_code == 200:
                    st.success("Search completed successfully.")
                    main()
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")

            except requests.exceptions.RequestException as e:
                st.error(f"Error while contacting backend: {str(e)}")

    else:
        st.warning("Please enter a search query")