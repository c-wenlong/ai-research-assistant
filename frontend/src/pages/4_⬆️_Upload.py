import json
import streamlit as st
import PyPDF2
import io
import pymongo
from openai import OpenAI

# Set page config to change the name in the sidebar
st.set_page_config(
    page_title="PDF Analyzer",  # This will appear in the sidebar and browser tab
    page_icon="📄",  # Optional: You can set an emoji or image URL as the page icon
    layout="wide",  # Optional: Use wide layout
    initial_sidebar_state="expanded",  # Optional: Start with sidebar expanded
)


# Set the sidebar title
st.sidebar.title("PDF Analyzer")  # This will appear in the sidebar
st.sidebar.write("Welcome to the PDF Analyzer tool!")
st.sidebar.write("Upload a PDF file to get started.")


# Get paper summary from openai model
def get_paper_summary(prompt, text):
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    try:
        # Call the OpenAI API with GPT-4
        userPrompt = (
            "Below is the paper, please fill in and return the JSON structure, and only output the JSON structure and no additional text. Remove ``` from the beginning and end of the JSON structure."
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


# Function to process the PDF file
def process_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    num_pages = len(pdf_reader.pages)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return num_pages, text


# Function to process the markdown file
def process_md(file_path):
    with open(file_path, "r") as file:
        return file.read()


# Function to process the JSON file
def process_json(summary):
    # Remove triple backticks and strip whitespace
    cleaned_summary = summary.strip().lstrip("`").rstrip("`").strip()

    # Debug: Print the first 100 characters of the cleaned summary
    st.text("First 100 characters of cleaned summary:")
    st.code(cleaned_summary[:100])

    # Debug: Print the length of the cleaned summary
    st.text(f"Length of cleaned summary: {len(cleaned_summary)}")

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


def push_data_to_mongodb(data: dict):
    if not isinstance(data, dict):
        raise ValueError("Input must be a dictionary")

    client = pymongo.MongoClient(st.secrets["MONGODB_URL"])

    db = client["research_articles"]
    collection = db["pdf_upload_papers"]

    # Insert data into the collection
    result = collection.insert_one(data)
    client.close()

    return result.inserted_id


st.title("PDF File Uploader and Processor")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    st.success("File successfully uploaded!")

    # Process the PDF & prompt MD
    num_pages, text = process_pdf(io.BytesIO(uploaded_file.getvalue()))
    st.success("Reading PDF!")

    # Get the prompt
    prompt = process_md("./frontend/src/assets/research-paper-summarization-prompt.md")

    # Get paper summary
    summary = get_paper_summary(prompt, text)

    # Format summary into JSON
    paper_data = process_json(summary)

    # Add in extra information
    paper_data["type"] = "pdf"

    # Display PDF information
    st.subheader("PDF Information")
    st.write(f"Number of pages: {num_pages}")

    # Add upload to MongoDB button
    if st.button("Upload to MongoDB"):
        try:
            inserted_id = push_data_to_mongodb(paper_data)
            st.success(f"File uploaded to MongoDB with ID: {inserted_id}")
        except Exception as e:
            st.error(f"An error occurred while uploading to MongoDB: {str(e)}")
else:
    st.info("Please upload a PDF file.")
