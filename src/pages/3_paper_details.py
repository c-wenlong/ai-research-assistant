import streamlit as st
import json
import pandas as pd
import os

# Function to load JSON files from a directory
def load_json_files(directory):
    json_files = {}
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r') as file:
                json_files[filename] = json.load(file)
    return json_files

# Load all JSON files from the directory
json_files = load_json_files('./assets/papers/')

# Add a "Clear selection" option to the file list
file_options = ["Clear selection"] + list(json_files.keys())

# Select a file
selected_file = st.selectbox('Select a paper', file_options)

# Function to truncate text
def truncate_text(text, max_words=50):
    words = text.split()
    if len(words) > max_words:
        return ' '.join(words[:max_words]) + '...'
    return text

# Streamlit app
st.title('Article Information')

# Check if a file is selected (not "Clear selection")
if selected_file != "Clear selection":
    # Get the data for the selected file
    data = json_files[selected_file]

    # Create a DataFrame
    df = pd.DataFrame([data])

    # Display basic information
    st.write(f"**PMC ID:** {df['pmc_id'].iloc[0]}")
    st.write(f"**Title:** {df['title'].iloc[0]}")
    st.write(f"**Abstract:** {df['abstract'].iloc[0]}")
    st.write(f"**Publication Date:** {df['publication_date'].iloc[0]}")
    st.write(f"**Journal Name:** {df['journal_name'].iloc[0]}")
    st.write(f"**DOI:** {df['doi'].iloc[0]}")

    # Display authors as multiselect
    st.write("**Authors:**")
    authors = st.multiselect('Select authors', df['authors'].iloc[0], df['authors'].iloc[0])
    for author in authors:
        st.markdown(f'<span style="background-color: #e6f3ff; padding: 2px 6px; border-radius: 10px;">{author}</span>', unsafe_allow_html=True)

    # Display keywords as multiselect
    st.write("**Keywords:**")
    keywords = df['keywords'].iloc[0]
    if keywords:  # Check if keywords exist
        selected_keywords = st.multiselect('Select keywords', keywords, keywords)
        for keyword in selected_keywords:
            st.markdown(f'<span style="background-color: #fff0e6; padding: 2px 6px; border-radius: 10px;">{keyword}</span>', unsafe_allow_html=True)
    else:
        st.write("No keywords available for this paper.")

    # Display truncated sections
    sections = ['Introduction', 'Methods', 'Results', 'Discussion', 'Conclusion']
    for section in sections:
        st.write(f"**{section}:**")
        st.write(truncate_text(df[section].iloc[0]))

    # Display references as multiselect
    st.write("**References:**")
    references = df['References'].iloc[0]
    if references:  # Check if references exist
        selected_references = st.multiselect('Select references', references, references)
        for ref in selected_references:
            st.markdown(f'<span style="background-color: #e6ffe6; padding: 2px 6px; border-radius: 10px;">{ref}</span>', unsafe_allow_html=True)
    else:
        st.write("No references available for this paper.")
else:
    st.write("No paper selected. Please choose a paper from the dropdown to view its details.")