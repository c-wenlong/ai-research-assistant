import streamlit as st
import json
import pandas as pd
import os
from st_aggrid import AgGrid, GridOptionsBuilder

# Set the page configuration
st.set_page_config(layout="wide", page_title="Table of Your Papers", page_icon="📚"),

# Helper functions
js_code = """
function(params) {
    if (params.value) {
        let items = Array.isArray(params.value) ? params.value : params.value.split(',').map(item => item.trim());
        return items.map(item => 
            '<span style="background-color: #e6f3ff; padding: 2px 6px; border-radius: 10px; margin: 2px; display: inline-block;">' + 
            item + '</span>'
        ).join(' ');
    }
    return 'None';
}
"""


# Function to truncate text
def truncate_text(text, max_words=50):
    words = text.split()
    if len(words) > max_words:
        return " ".join(words[:max_words]) + "..."
    return text


# Function to load JSON files from a directory
def load_json_files(directory):
    json_files = {}
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print("Script directory:", script_dir)
    assets_dir = os.path.join(script_dir, directory)
    print("Assets directory:", assets_dir)

    for filename in os.listdir(assets_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(
                assets_dir, filename
            )  # Use assets_dir here, not directory
            print(f"Loading file: {file_path}")
            with open(file_path, "r") as file:
                json_files[filename] = json.load(file)
    return json_files


# Function to create a multiselect component NEED TO FIX
def create_multiselect(options):
    return options if options else []


# Main functions
def load_json():
    # Load all JSON files from the directory
    json_files = load_json_files(st.secrets["PDF_PATH"])

    # Process all files
    all_data = []
    for filename, data in json_files.items():
        display_data = {
            # "Filename": filename,
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


def load_table(all_data):
    # Create a DataFrame from the processed data
    display_df = pd.DataFrame(all_data)

    # Create a grid options builder
    gb = GridOptionsBuilder.from_dataframe(display_df)

    # Configure page options
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar(
        filters_panel=True, columns_panel=True, defaultToolPanel="filters"
    )

    # Configure the grid options
    gb.configure_default_column(
        wrapText=True, autoHeight=True, maxWidth=500, groupable=True
    )
    gb.configure_column("Authors", cellRenderer=js_code, minWidth=300)
    gb.configure_column("Keywords", cellRenderer=js_code, minWidth=300)
    gb.configure_column("References", cellRenderer=js_code, minWidth=300)
    gb.configure_column("Title", minWidth=400)
    gb.configure_column("Abstract", minWidth=500)
    gb.configure_grid_options(enableRangeSelection=True)
    gridOptions = gb.build()

    # Display the table
    AgGrid(
        display_df,
        gridOptions=gridOptions,
        fit_columns_on_grid_load=False,
        enable_enterprise_modules=True,
        allow_unsafe_jscode=True,  # Add this line
    )


def main():
    st.title("Your Papers")
    all_data = load_json()
    load_table(all_data)


main()
