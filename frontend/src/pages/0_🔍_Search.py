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


# Function to process the JSON file
def process_json(current_trends):
    # Remove triple backticks and strip whitespace
    cleaned_summary = current_trends.strip().lstrip("`").rstrip("`").strip()

    try:
        # Attempt to parse the JSON
        paper_data = json.loads(cleaned_summary)
        return paper_data
    except json.JSONDecodeError as e:
        st.error(f"Error parsing JSON: {str(e)}")

        # Debug: Show the problematic part of the JSON
        error_position = e.pos
        start = max(0, error_position - 20)
        end = min(len(cleaned_summary), error_position + 20)
        problematic_part = cleaned_summary[start:end]
        st.text("Problematic part of the JSON:")
        st.code(f"...{problematic_part}...")

        # If the string is empty, show a specific message
        if not cleaned_summary:
            st.error("The cleaned summary is empty. Please check the input data.")

        # Show the full cleaned summary for manual inspection
        st.text("Full cleaned summary:")
        st.code(cleaned_summary)

        return None


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
def get_current_trends_and_insights(prompt, text, topic):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    try:
        # Call the OpenAI API with GPT-4
        userPrompt = (
            f"Analyze the research papers and conduct a web search on {topic}. "
            f"Provide up to 5 entries of current trends, missing gaps, and future developments "
            f"related to this topic in the specified JSON format "
            f"and only output the JSON structure and no additional text. Remove ``` from the beginning and end of the JSON structure."
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
        client.close()
        return response.choices[0].message.content

    except Exception as e:
        print(f"Error occurred: {e}")
        return None


def display_trends_table(current_trends):
    display_df = pd.DataFrame(current_trends)
    # Define the new column names
    new_column_names = ["Current Trends", "Missing Gaps", "Future Developments"]

    # Rename the columns
    display_df.columns = new_column_names
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

    gridOptions = gb.build()
    AgGrid(
        display_df,
        gridOptions=gridOptions,
        fit_columns_on_grid_load=False,
        enable_enterprise_modules=True,
        height=500,
        theme="streamlit",
        allow_unsafe_jscode=True,  # This is needed for custom JavaScript renderers
    )


# Optional: Add a title before the table
st.title("Current Trends, Missing Gaps, and Future Developments")

# Define the backend endpoint (replace with your actual endpoint URL)
BACKEND_URL = "http://127.0.0.1:5000/web_search"

# Minimalistic search bar UI
search_query = st.text_input("Enter your search query", "")


def main():
    message_placeholder = st.empty()
    message_placeholder.success("Fetching articles and summarizing them...")
    st.subheader("Top Research Articles from PubMed")
    all_data = load_database_pubmed()
    message_placeholder.success("Fetch successful!")
    load_table(all_data, "pubmed")
    message_placeholder.empty()

    # Create current trends and insights
    st.title("Current Trends and Insights")
    success_placeholder = st.empty()

    with st.spinner("Generating current trends and insights..."):
        prompt = process_md("./frontend/src/assets/research-analysis-prompt.md")
        processed_data = json_to_text(all_data)
        current_trends = get_current_trends_and_insights(
            prompt, processed_data, search_query
        )
        processed_current_trends = process_json(current_trends)
        display_trends_table(processed_current_trends)
        
    success_placeholder.success("Loading complete!")
    time.sleep(3)
    success_placeholder.empty()


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
                    main()
                    """
                    # Reading the streamed response
                    for chunk in response.iter_lines():
                        if chunk:
                            # Decode the chunk and process it as per backend response structure
                            result = json.loads(chunk.decode("utf-8"))
                            st.write(result)
                            time.sleep(1)  # Simulate delay between chunks
                    """
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")

            except requests.exceptions.RequestException as e:
                st.error(f"Error while contacting backend: {str(e)}")

    else:
        st.warning("Please enter a search query")

main()
