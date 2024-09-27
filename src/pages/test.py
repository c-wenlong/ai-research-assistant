import streamlit as st

# Custom CSS for chip style (single row container)
st.markdown(
    """
    <style>
    .chip-container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px; /* Space between chips */
        margin-bottom: 20px;
    }
    .chip {
        display: inline-block;
        padding: 0 15px;
        height: 30px;
        font-size: 14px;
        line-height: 30px;
        border-radius: 15px;
        background-color: #f1f1f1;
        margin: 5px;
        color: black;
        white-space: nowrap;  /* Prevent text wrapping within the chip */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# List of options to display as chips
options = ["Chip 1", "Chip 2", "Chip 3", "Chip 4", "Chip 5", "Chip 6","Chip 1", "Chip 2", "Chip 3", "Chip 4", "Chip 5", "Chip 6","Chip 1", "Chip 2", "Chip 3", "Chip 4", "Chip 5", "Chip 6","Chip 1", "Chip 2", "Chip 3", "Chip 4", "Chip 5", "Chip 6","Chip 1", "Chip 2", "Chip 3", "Chip 4", "Chip 5", "Chip 6","Chip 1", "Chip 2", "Chip 3", "Chip 4", "Chip 5", "Chip 6"]

# Render chips in a single row
st.write("Available Chips:")
chip_container_html = '<div class="chip-container">'
for option in options:
    chip_container_html += f'<div class="chip">{option}</div>'
chip_container_html += '</div>'

# Display the chip container
st.markdown(chip_container_html, unsafe_allow_html=True)
