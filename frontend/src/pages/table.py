import streamlit as st
import json
import pandas as pd
import os
from st_aggrid import AgGrid, GridOptionsBuilder


# Function to load JSON files from a directory
def load_json_files(directory):
    json_files = {}
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)
            with open(file_path, "r") as file:
                json_files[filename] = json.load(file)
    return json_files


# Function to truncate text
def truncate_text(text, max_words=50):
    words = str(text).split()
    if len(words) > max_words:
        return " ".join(words[:max_words]) + "..."
    return text


# Function to create a multiselect component
def create_multiselect(options):
    if options:
        return ", ".join(
            [
                f'<span style="background-color: #e6f3ff; padding: 2px 6px; border-radius: 10px;">{item}</span>'
                for item in options
            ]
        )
    return "None"


# Load all JSON files from the directory
json_files = load_json_files("../assets/papers/")

# Streamlit app
st.set_page_config(layout="wide")  # Set the layout to wide mode
st.title("Papers")

# Process all files
all_data = []
for filename, data in json_files.items():
    display_data = {
        "Filename": filename,
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

# Create a DataFrame from the processed data
display_df = pd.DataFrame(all_data)

# Create a grid options builder
gb = GridOptionsBuilder.from_dataframe(display_df)
gb.configure_default_column(wrapText=True, autoHeight=True, minWidth=200)
gb.configure_column("Authors", cellRenderer="html", minWidth=300)
gb.configure_column("Keywords", cellRenderer="html", minWidth=300)
gb.configure_column("References", cellRenderer="html", minWidth=300)
gb.configure_column("Title", minWidth=400)
gb.configure_column("Abstract", minWidth=500)
gb.configure_grid_options(enableRangeSelection=True)
gridOptions = gb.build()

# Display the table
AgGrid(
    display_df,
    gridOptions=gridOptions,
    height=800,
    fit_columns_on_grid_load=False,
    enable_enterprise_modules=True,
)
