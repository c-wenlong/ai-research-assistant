import os
import streamlit as st
import pandas as pd
import pymongo
from bson import ObjectId

# Custom CSS to make content full-width
st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)


# Function to fetch papers from MongoDB
def fetch_papers_from_mongodb_pubmed():
    client = pymongo.MongoClient(os.getenv("MONGODB_URL"))
    db = client["research_articles"]
    collection = db["summarized_fields_article"]
    papers = list(collection.find())
    client.close()
    return papers


# Function to fetch papers from MongoDB
def fetch_papers_from_mongodb_pdf():
    client = pymongo.MongoClient(os.getenv("MONGODB_URL"))
    db = client["research_articles"]
    collection = db["pdf_upload_papers"]
    papers = list(collection.find())
    client.close()
    return papers


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


# Fetch papers from MongoDB
papers = fetch_papers_from_mongodb_pdf()

# Create a list of paper titles for the dropdown
paper_titles = [""] + [paper["title"] for paper in papers]

# Streamlit app
st.title("Article Information")

# Select a paper
selected_title = st.selectbox("Select a paper", paper_titles)

# Check if a paper is selected
if selected_title:
    # Find the selected paper in the list
    selected_paper = next(
        (paper for paper in papers if paper["title"] == selected_title), None
    )

    if selected_paper:
        # Create a DataFrame
        df = pd.DataFrame([selected_paper])

        # Display basic information
        st.markdown(f"**Title:** {df['title'].iloc[0]}")
        st.markdown(f"**Abstract:** {df['abstract'].iloc[0]}")
        st.markdown(f"**Publication Date:** {df['publication_date'].iloc[0]}")
        st.markdown(f"**Journal Name:** {df['journal_name'].iloc[0]}")
        st.markdown(f"**DOI:** {df['doi'].iloc[0]}")

        # Display authors as multiselect
        st.markdown("**Authors:**")
        authors = st.multiselect(
            "Select authors", df["authors"].iloc[0], df["authors"].iloc[0]
        )

        # Display keywords as multiselect
        st.markdown("**Keywords:**")
        keywords = df["keywords"].iloc[0]
        if keywords:
            selected_keywords = st.multiselect("Select keywords", keywords, keywords)
        else:
            st.markdown("No keywords available for this paper.")

        # Display truncated sections
        sections = ["introduction", "methods", "results", "discussion", "conclusion"]
        for section in sections:
            st.markdown(f"**{section.capitalize()}:**")
            st.markdown(df[section].iloc[0])

        # Display references as multiselect
        st.markdown("**References:**")
        references = df["references"].iloc[0]
        if references:
            formatted_reference = format_reference(references)
            st.write(formatted_reference)
        else:
            st.markdown("No references available for this paper.")
    else:
        st.markdown("Error: Selected paper not found in the database.")
else:
    st.markdown(
        "No paper selected. Please choose a paper from the dropdown to view its details."
    )
