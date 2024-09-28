import streamlit as st
import pandas as pd
from PIL import Image
import plotly.express as px

st.set_page_config(
    page_title="AIRA - Artificial Intelligence Research Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.sidebar.title("AIRA")
st.sidebar.markdown("Your Intelligent Research Assistant")

# Placeholder image
st.image(
    "./frontend/src/assets/images/neil-degrasse-tyson.jpg",
)

st.title("Welcome to AIRA: Artificial Intelligence Research Assistant")
st.markdown(
    """
AIRA is your comprehensive tool for managing, analyzing, and interacting with research papers. 
Whether you're a seasoned researcher or just starting your academic journey, AIRA is designed to 
streamline your research process and enhance your understanding of scientific literature.
"""
)

st.header("Key Features")

# Interactive feature showcase
features = {
    "🔍 Smart Search": "Find relevant research papers easily",
    "🗒️ Interactive Table": "Explore your literature database",
    "📜 Detailed Paper Analysis": "Dive deep into individual papers",
    "⬆️ PDF Upload and Analysis": "Analyze and summarize your PDFs",
    "🤖 AI-Powered Chatbot": "Get insights and ask questions",
    "🧠 Knowledge Graph": "Visualize research connections",
}

selected_feature = st.selectbox(
    "Select a feature to learn more:", list(features.keys())
)
st.info(features[selected_feature])

# Sample interactive element: Paper count by year
st.header("Research Paper Statistics")
years = range(2015, 2024)
paper_counts = [120, 150, 200, 180, 250, 300, 280, 350, 400]
df = pd.DataFrame({"Year": years, "Paper Count": paper_counts})

fig = px.bar(df, x="Year", y="Paper Count", title="Papers Analyzed by Year")
st.plotly_chart(fig)

# Getting Started section with expandable content
st.header("Getting Started")
with st.expander("How to use AIRA"):
    st.markdown(
        """
    1. Use the sidebar to navigate between different features.
    2. Start by uploading a paper or searching for existing papers in our database.
    3. Explore the interactive table to get an overview of available literature.
    4. Use the chatbot to ask questions or get insights about specific papers.
    5. Visualize connections using the knowledge graph to discover new research directions.
    """
    )

# Call-to-action
st.success("Ready to revolutionize your research? Get started with AIRA today!")

# Feedback section
st.header("We Value Your Feedback")
feedback = st.text_area("Share your thoughts or suggestions:")
if st.button("Submit Feedback"):
    st.toast("Thank you for your feedback!")

st.info("👈 Select a feature from the sidebar to get started!")
