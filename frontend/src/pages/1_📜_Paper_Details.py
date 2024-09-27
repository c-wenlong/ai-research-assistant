import streamlit as st
import json
import pandas as pd
import os

# Custom CSS to make content full-width
st.markdown("""
<style>
.reportview-container .main .block-container {
    max-width: 1000px;
    padding-top: 2rem;
    padding-right: 2rem;
    padding-left: 2rem;
    padding-bottom: 2rem;
}
.stSelectbox [data-baseweb="select"] {
    max-width: 1000px;
}
.stMultiSelect [data-baseweb="select"] {
    max-width: 1000px;
}
</style>
""", unsafe_allow_html=True)

# Function to load JSON files from a directory
def load_json_files(directory):
    json_files = {}
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print("Script directory:", script_dir)
    assets_dir = os.path.join(script_dir, directory)
    print("Assets directory:", assets_dir)

    for filename in os.listdir(assets_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(assets_dir, filename)
            print(f"Loading file: {file_path}")
            with open(file_path, "r") as file:
                json_files[filename] = json.load(file)
    return json_files

# Load all JSON files from the directory
json_files = load_json_files('../assets/papers/')

# Add a "Clear selection" option to the file list
file_options = [" "] + list(json_files.keys())

# Select a file
selected_file = st.selectbox('Select a paper', file_options)

# Streamlit app
st.title('Article Information')

# Check if a file is selected (not "Clear selection")
if selected_file != " ":
    # Get the data for the selected file
    data = json_files[selected_file]

    # Create a DataFrame
    df = pd.DataFrame([data])

    # Display basic information
    st.markdown(f"**PMC ID:** {df['pmc_id'].iloc[0]}")
    st.markdown(f"**Title:** {df['title'].iloc[0]}")
    st.markdown(f"**Abstract:** {df['abstract'].iloc[0]}")
    st.markdown(f"**Publication Date:** {df['publication_date'].iloc[0]}")
    st.markdown(f"**Journal Name:** {df['journal_name'].iloc[0]}")
    st.markdown(f"**DOI:** {df['doi'].iloc[0]}")

    # Display authors as multiselect
    st.markdown("**Authors:**")
    authors = st.multiselect('Select authors', df['authors'].iloc[0], df['authors'].iloc[0])

    # Display keywords as multiselect
    st.markdown("**Keywords:**")
    keywords = df['keywords'].iloc[0]
    if keywords:  # Check if keywords exist
        selected_keywords = st.multiselect('Select keywords', keywords, keywords)
        keyword_html = ' '.join([f'<span style="background-color: #fff0e6; padding: 2px 6px; border-radius: 10px; margin-right: 5px;">{keyword}</span>' for keyword in selected_keywords])
        st.markdown(keyword_html, unsafe_allow_html=True)
    else:
        st.markdown("No keywords available for this paper.")

    # Display truncated sections
    sections = ['Introduction', 'Methods', 'Results', 'Discussion', 'Conclusion']
    for section in sections:
        st.markdown(f"**{section}:**")
        st.markdown(df[section].iloc[0])

    # Display references as multiselect
    st.markdown("**References:**")
    references = df['References'].iloc[0]
    if references:  # Check if references exist
        selected_references = st.multiselect('Select references', references, references)
        reference_html = ' '.join([f'<span style="background-color: #e6ffe6; padding: 2px 6px; border-radius: 10px; margin-right: 5px;">{ref}</span>' for ref in selected_references])
        st.markdown(reference_html, unsafe_allow_html=True)
    else:
        st.markdown("No references available for this paper.")
else:
    st.markdown("No paper selected. Please choose a paper from the dropdown to view its details.")