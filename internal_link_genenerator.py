import streamlit as st
import csv
import re
from urllib.parse import urlparse
from io import StringIO
import pandas as pd
import base64

# --- Core Logic Functions (No Change) ---

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
    
    return output.getvalue()

def copy_to_sheets_button(csv_string):
    """Injects HTML and JS for a custom light blue copy-to-sheets button."""
    
    # Base64 encode the CSV string to safely pass it through the HTML attribute
    b64_csv = base64.b64encode(csv_string.encode('utf-8')).decode('utf-8')
    
    js_code = f"""
    <script>
        function copyToClipboard(b64Data) {{
            const csvData = atob(b64Data);
            navigator.clipboard.writeText(csvData)
                .then(() => {{
                    // Display temporary success message
                    const successDiv = document.createElement('div');
                    successDiv.innerHTML = '<div style="background-color: #c8e6c9; color: #155724; padding: 12px; border-radius: 4px; margin-top: 16px; font-size: 0.9em; text-align: left;">Data copied to clipboard! Paste directly into Google Sheets.</div>';
                    document.querySelector('.copy-to-sheets-placeholder').appendChild(successDiv);
                    setTimeout(() => successDiv.remove(), 3000); 
                }})
                .catch(err => {{
                    alert('Could not copy text: ' + err);
                }});
        }}
    </script>
    <div class="copy-to-sheets-placeholder"></div>
    <button class="copy-to-sheets-btn stButton button" onclick="copyToClipboard('{b64_csv}')">
        Copy to Sheets (CSV)
    </button>
    """
    st.markdown(js_code, unsafe_allow_html=True)


# --- Streamlit UI ---

def app():
    # Initialize session state for generated links
    if 'generated_links' not in st.session_state:
        st.session_state['generated_links'] = None
    
    # --- PAGE CONFIGURATION & CUSTOM CSS ---
    st.set_page_config(
        page_title="Internal Link Generator", 
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Archivo:wght@400;700&display=swap');

        /* 1. Overall App Background (Dark Pink) */
        .stApp {
            background-color: #ffc0cb; /* Dark Pink */
            font-family: 'Archivo', sans-serif;
        }

        /* 2. Light Pink Container Box (Surface) */
        .main .block-container {
            background-color: #ffe0eb; /* Light Pink */
            border-radius: 8px; /* Standard Material rounding */
            padding: 32px; /* Consistent spacing (multiple of 8) */
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15); /* Material Elevation 2-3 equivalent */
            margin-top: 24px;
            margin-bottom: 24px;
        }

        /* Centered H1 Heading Styling */
        h1 {
            color: #6A1F8D;
            font-size: 2em; /* Adjusted slightly smaller for Material text scale */
            margin-bottom: 8px; /* Consistent spacing */
        }
        p {
            margin-bottom: 24px; /* Consistent spacing */
            font-size: 1.05em;
        }
        
        /* Text Area Styling */
        .stTextArea textarea {
            border-radius: 4px; /* Material standard rounding */
            border: 1px solid #ffabab; 
            padding: 12px;
            box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.06); /* Subtle inner shadow for depth */
        }

        /* General Button Styling */
        .stButton button, .stDownloadButton button, .copy-to-sheets-btn {
            border-radius: 20px !important; /* Pill shape for action buttons */
            font-weight: 700;
            padding: 12px 20px; /* Consistent padding */
            transition: all 0.2s ease-out;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* Subtle elevation */
            margin: 8px; /* Consistent spacing */
            border: none;
            color: white !important; 
        }
        .stButton button:hover, .stDownloadButton button:hover, .copy-to-sheets-btn:hover {
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); /* Higher elevation on hover */
            transform: translateY(-2px);
        }

        /* Generate Links Button (Pink) */
        .stButton button[kind="primary"] {
            background-color: #ff69b4 !important; 
        }

        /* Download CSV Button (Purple) */
        .stDownloadButton button {
            background-color: #9c27b0 !important; 
        }

        /* Copy to Sheets Button (Light Blue) */
        .copy-to-sheets-btn {
            background-color: #87CEEB !important;
        }
        
        /* DataFrame Styling */
        .stDataFrame {
            margin-top: 24px;
        }
        /* Table Header Styling (Purple, Larger Font) */
        .stDataFrame th {
            background-color: #6A1F8D !important;
            color: white !important;
            font-size: 1.05em !important; /* Material Standard font size balance */
            padding: 16px 12px !important; /* Uniform spacing */
        }
        /* Table Body Cells */
        .stDataFrame td {
            padding: 12px !important; /* Consistent spacing */
            font-size: 0.95em !important;
        }
        
        /* Instructions Styling */
        .instructions-list li {
            background-color: #fcf4f7; /* Very light pink/surface color */
            margin-bottom: 8px;
            padding: 16px; 
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05); /* Very low elevation */
            font-size: 1em;
        }
        </style>
        """, unsafe_allow_html=True
    )

    # --- APP HEADER ---
    st.markdown(f"""
        <h1 style='color: #6A1F8D; text-align: center;'>
            🔗 BIDIRECTIONAL INTERNAL LINK GENERATOR 🚀
        </h1>
        <p style='text-align: center;'>
            Streamline your SEO efforts by quickly generating all possible internal linking variations.
        </p>
    """, unsafe_allow_html=True)
    
    # --- URL INPUT AREA ---
    urls_input = st.text_area(
        "Enter URLs (one per line):", 
        height=180,
        placeholder="https://example.com/topic-a-guide\nhttps://example.com/blog-post-on-topic-b\nhttps://example.com/service-page-c",
        key="url_input_area",
        help="Paste a list of full URLs (e.g., https://example.com/page)."
    )

    # --- BUTTONS ROW (Defined up front to ensure Above the Fold placement) ---
    st.markdown("<h3 style='color: #555; margin-top: 8px; margin-bottom: 8px; font-size: 1.1em;'>Actions:</h3>", unsafe_allow_html=True)
    
    btn_col1, btn_col2, btn_col3 = st.columns([0.25, 0.3, 0.45]) 
    
    # 1. Generate Links Button (Pink) - Primary button
    if btn_col1.button("Generate Links", key="generate_btn", type="primary"):
        urls = [
            url.strip() 
            for url in urls_input.split('\n') 
            if url.strip().startswith(('http://', 'https://'))
        ]

        if len(urls) < 2:
            st.session_state['generated_links'] = []
            st.error("Please enter at least two valid URLs (starting with http:// or https://) to generate links.")
        else:
            link_data = generate_links(urls)
            st.session_state['generated_links'] = link_data
            st.success(f"Success! Generated {len(link_data)} bidirectional link rows.")
            
    # --- Conditional Display of Export Buttons and Results ---
    if st.session_state['generated_links'] and len(st.session_state['generated_links']) > 0:
        
        csv_string = convert_to_csv(st.session_state['generated_links'])
        
        # 2. Download CSV Button (Purple)
        btn_col2.download_button(
            label="Download CSV Data",
            data=csv_string.encode('utf-8'),
            file_name='internal_links_output.csv',
            mime='text/csv',
            key='download_csv_btn'
        )
        
        # 3. Copy to Sheets Button (Light Blue)
        with btn_col3:
            copy_to_sheets_button(csv_string)

        # --- RESULTS DISPLAY ---
        st.markdown("<h3 style='color: #555; margin-top: 32px; font-size: 1.1em;'>Generated Results Table:</h3>", unsafe_allow_html=True)
        
        # Display as a DataFrame
        df_display = pd.DataFrame(st.session_state['generated_links'])
        st.dataframe(df_display, hide_index=True, use_container_width=True)
    
    # --- INSTRUCTIONS AT THE BOTTOM ---
    st.markdown("<hr style='border-top: 1px solid #ffabab; margin-top: 48px; margin-bottom: 24px;'>", unsafe_allow_html=True)
    st.markdown("<h2 class='instructions-header' style='font-size: 1.5em; text-align: center; color: #6A1F8D;'>How to Use This Tool:</h2>", unsafe_allow_html=True)
    st.markdown(
        """
        <ul class='instructions-list'>
            <li><strong>Step 1: Prepare Your URLs</strong><br>
                Gather the complete list of URLs. They must start with <code>http://</code> or <code>https://</code>.
            </li>
            <li><strong>Step 2: Generate & Review</strong><br>
                Paste the list into the box and click the **Generate Links** button. The results table will display all reciprocal pairs.
            </li>
            <li><strong>Step 3: Export Data</strong><br>
                Use the buttons above the table to export the data:
                <ul>
                    <li>**Download CSV Data (Purple)**: Saves a file locally.</li>
                    <li>**Copy to Sheets (CSV) (Light Blue)**: Copies data to your clipboard for instant pasting into Google Sheets.</li>
                </ul>
            </li>
        </ul>
        """, unsafe_allow_html=True
    )

if __name__ == "__main__":
    app()
