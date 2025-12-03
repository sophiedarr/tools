import streamlit as st
import csv
import re
from urllib.parse import urlparse
from io import StringIO

# --- Core Logic Functions ---

def extract_slug(url):
    """
    Tries to extract a clean, capitalized slug/keyword from the URL path.
    """
    try:
        parsed_url = urlparse(url)
        path = parsed_url.path.strip('/')
        segments = path.split('/')
        
        slug = ''
        if segments and segments[-1]:
            slug = segments[-1]
        elif len(segments) > 1 and segments[-2]:
            slug = segments[-2]

        if not slug:
            return 'Link'

        slug = re.sub(r'\.[^/.]+$', '', slug)
        slug = re.sub(r'[-_]', ' ', slug)
        
        formatted_slug = ' '.join(word.capitalize() for word in slug.split())
        return formatted_slug if formatted_slug else 'Link'

    except Exception:
        return 'Link'

def generate_links(urls):
    """
    Generates all bidirectional internal link variations for a list of URLs.
    """
    link_data = []

    for i in range(len(urls)):
        for j in range(len(urls)):
            if i == j:
                continue

            source_url = urls[i]
            target_url = urls[j]

            suggested_anchor = extract_slug(target_url)
            link_html = f'<a href="{target_url}">{suggested_anchor}</a>'

            link_data.append({
                "Source URL": source_url,
                "Target URL": target_url,
                "Suggested Anchor Text (Placeholder)": suggested_anchor,
                "Link HTML": link_html,
            })
            
    return link_data

def convert_to_csv(link_data):
    """Converts the list of dictionaries into a CSV string."""
    output = StringIO()
    fieldnames = ["Source URL", "Target URL", "Suggested Anchor Text (Placeholder)", "Link HTML"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    
    writer.writeheader()
    writer.writerows(link_data)
    
    return output.getvalue().encode('utf-8')

# --- Streamlit UI ---

def app():
    # Set page configuration for wide mode and initial styling
    st.set_page_config(
        page_title="Internal Link Generator", 
        layout="wide", # This makes the app expand to full width
        initial_sidebar_state="collapsed"
    )

    # Inject custom CSS for desired styling
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Archivo:wght@400;700&display=swap');

        body {
            font-family: 'Archivo', sans-serif;
            background-color: #ffe0eb; /* Light pink background */
            color: #333;
        }
        .stApp {
            background-color: #ffe0eb; /* Ensure Streamlit's main app container also uses light pink */
            font-family: 'Archivo', sans-serif;
            color: #333;
        }
        h1 {
            color: #6A1F8D; /* Deep Violet/Plum for heading */
            text-align: center;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            font-family: 'Archivo', sans-serif;
        }
        .stTextArea textarea {
            border-radius: 8px; /* Rounded edges for textarea */
            border: 1px solid #ffabab; /* Pink border */
            font-family: 'Archivo', sans-serif;
        }
        /* Custom button styling */
        .stButton button {
            border-radius: 25px; /* Rounded edges for buttons */
            font-weight: bold;
            font-family: 'Archivo', sans-serif;
            padding: 0.5em 1.2em; /* Adjust padding for better look */
            transition: background-color 0.3s ease, transform 0.2s ease;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        /* Style for the Generate Links button (pink) */
        .stButton button[kind="primary"] { /* Targeting the 'primary' button type */
            background-color: #ff69b4; /* Pink */
            color: white;
            border: none;
        }
        .stButton button[kind="primary"]:hover {
            background-color: #e65a9e;
            transform: translateY(-2px);
            color: white; /* Keep text white on hover */
        }
        /* Style for the Download CSV button (purple) */
        .stDownloadButton button { /* Streamlit download button has a different class */
            background-color: #9c27b0; /* Purple */
            color: white;
            border: none;
        }
        .stDownloadButton button:hover {
            background-color: #7b1fa2;
            transform: translateY(-2px);
            color: white; /* Keep text white on hover */
        }
        .stAlert {
            border-radius: 8px; /* Rounded alerts */
        }
        p {
            font-family: 'Archivo', sans-serif;
            line-height: 1.6;
        }
        /* Adjusting for dataframe to remove scrollbar if possible and make it wide */
        .stDataFrame {
            width: 100% !important;
        }
        .stDataFrame > div > div > div > div > div {
            overflow-x: hidden !important; /* Hide dataframe internal scrollbar if not needed */
        }
        </style>
        """, unsafe_allow_html=True
    )

    # App title and description
    st.markdown(f"""
        <h1 style='color: #6A1F8D; text-align: center;'>
            🔗 BIDIRECTIONAL INTERNAL LINK GENERATOR 🚀
        </h1>
        <p style='text-align: center;'>
            Paste your list of complete URLs below (one per line).
        </p>
    """, unsafe_allow_html=True)
    
    # Input Area
    urls_input = st.text_area(
        "Enter URLs:", 
        height=150, 
        placeholder="https://example.com/page-1\nhttps://example.com/page-2\nhttps://example.com/page-3",
        key="url_input_area"
    )

    # Use columns to place buttons side-by-side
    col1, col2, col3 = st.columns([0.2, 0.3, 0.5]) # Adjust column ratios if needed

    # Generate Links Button (Pink)
    if col1.button("Generate Links", key="generate_btn", type="primary"):
        st.session_state['generated_links'] = None # Clear previous state
        # Process and filter URLs
        urls = [
            url.strip() 
            for url in urls_input.split('\n') 
            if url.strip().startswith(('http://', 'https://'))
        ]

        if len(urls) < 2:
            st.error("Please enter at least two valid URLs (starting with http:// or https://) to generate links.")
        else:
            # Generate data
            link_data = generate_links(urls)
            st.session_state['generated_links'] = link_data # Store in session state
            st.success(f"Success! Generated {len(link_data)} bidirectional link rows.")
            
    # Check if links have been generated to show the download button
    if 'generated_links' in st.session_state and st.session_state['generated_links']:
        st.subheader("Generated Links")
        st.dataframe(st.session_state['generated_links'], hide_index=True, use_container_width=True)
        
        csv_data = convert_to_csv(st.session_state['generated_links'])
        
        # Download CSV Button (Purple) - sits next to Generate Links
        col2.download_button(
            label="Download CSV Data",
            data=csv_data,
            file_name='internal_links_output.csv',
            mime='text/csv',
            key='download_csv_btn'
        )

if __name__ == "__main__":
    app()
