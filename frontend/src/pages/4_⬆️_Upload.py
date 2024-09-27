import streamlit as st
import PyPDF2
import io

# Set page config to change the name in the sidebar
st.set_page_config(
    page_title="PDF Analyzer",  # This will appear in the sidebar and browser tab
    page_icon="📄",  # Optional: You can set an emoji or image URL as the page icon
    layout="wide",  # Optional: Use wide layout
    initial_sidebar_state="expanded"  # Optional: Start with sidebar expanded
)


# Set the sidebar title
st.sidebar.title("PDF Analyzer")  # This will appear in the sidebar

# You can also add other sidebar elements here
st.sidebar.write("Welcome to the PDF Analyzer tool!")
st.sidebar.write("Upload a PDF file to get started.")

def process_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    num_pages = len(pdf_reader.pages)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return num_pages, text

st.title("PDF File Uploader and Processor")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    st.success("File successfully uploaded!")
    
    # Display file details
    file_details = {
        "Filename": uploaded_file.name,
        "File size": f"{uploaded_file.size / 1024:.2f} KB",
        "File type": uploaded_file.type
    }
    st.write(file_details)
    
    # Process the PDF
    num_pages, text = process_pdf(io.BytesIO(uploaded_file.getvalue()))
    
    # Display PDF information
    st.subheader("PDF Information")
    st.write(f"Number of pages: {num_pages}")
    
    # Display extracted text
    st.subheader("Extracted Text (first 500 characters)")
    st.text_area("", text[:500], height=200)
    
    # Option to display full text
    if st.checkbox("Show full text"):
        st.text_area("Full Text", text, height=300)
else:
    st.info("Please upload a PDF file.")