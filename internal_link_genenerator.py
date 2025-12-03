import streamlit as st
import csv
import re
from urllib.parse import urlparse
from io import StringIO
import pandas as pd

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
    # --- PAGE CONFIGURATION ---
    st.set_page_config(
        page_title="Internal Link Generator", 
        layout="wide", # This makes the app expand to full width
        initial_sidebar_state="collapsed"
    )

    # --- CUSTOM CSS INJECTION ---
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Archivo:wght@400;700&display=swap');

        /* Overall App Background (Dark Pink) */
        .stApp {
            background-color: #ffc0cb; /* Darker Pink */
            font-family: 'Archivo', sans-serif;
            color: #333;
        }

        /* Container for the tool (Light Pink Box with Rounded Corners) */
        .main .block-container {
            background-color: #ffe0eb; /* Light Pink */
            border-radius: 15px; /* Rounded corners */
            padding: 30px; /* Adjust padding inside the box */
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2); /* Subtle shadow for depth */
            margin-top: 20px;
            margin-bottom: 20px;
        }

        /* Centered H1 Heading Styling */
        h1 {
            color: #6A1F8D; /* Deep Violet/Plum for heading */
            text-align: center;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            font-family: 'Archivo', sans-serif;
            font-size: 2.5em; /* Larger heading */
        }
        p {
            font-family: 'Archivo', sans-serif;
            line-height: 1.6;
            text-align: center; /* Center introductory paragraph */
            font-size: 1.1em;
            margin-bottom: 20px;
        }

        /* Text Area Styling */
        .stTextArea textarea {
            border-radius: 8px; /* Rounded edges for textarea */
            border: 1px solid #ffabab; /* Pink border */
            font-family: 'Archivo', sans-serif;
            padding: 12px;
            font-size: 1em;
        }
        .stTextArea label {
            font-size: 1.2em; /* Larger label for textarea */
            font-weight: bold;
            color: #555;
            margin-bottom: 8px;
        }

        /* Custom button styling */
        .stButton button {
            border-radius: 25px; /* Rounded edges for buttons */
            font-weight: bold;
            font-family: 'Archivo', sans-serif;
            padding: 0.8em 1.5em; /* Increased padding for larger buttons */
            transition: background-color 0.3s ease, transform 0.2s ease, color 0.3s ease;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            margin: 5px; /* Spacing between buttons */
            cursor: pointer;
            border: none; /* Remove default border */
        }
        
        /* Generate Links Button (Pink) */
        .stButton button[kind="primary"] {
            background-color: #ff69b4; /* Pink */
            color: white;
        }
        .stButton button[kind="primary"]:hover {
            background-color: #e65a9e;
            transform: translateY(-2px);
            color: white;
        }

        /* Download CSV Button (Purple) */
        .stDownloadButton button {
            background-color: #9c27b0; /* Purple */
            color: white;
        }
        .stDownloadButton button:hover {
            background-color: #7b1fa2;
            transform: translateY(-2px);
            color: white;
        }

        /* Copy to Sheets Button (Light Blue) - Custom Class */
        .stButton button.copy-to-sheets-btn {
            background-color: #87CEEB; /* Light Blue */
            color: white;
        }
        .stButton button.copy-to-sheets-btn:hover {
            background-color: #6495ED; /* Slightly darker blue */
            transform: translateY(-2px);
            color: white;
        }

        /* Alerts and Success Messages */
        .stAlert {
            border-radius: 8px;
            font-size: 1.1em;
            margin-top: 15px;
            margin-bottom: 15px;
        }

        /* DataFrame Styling */
        .stDataFrame {
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-top: 25px;
        }
        /* Table Header Styling (Purple, Larger Font) */
        .stDataFrame th {
            background-color: #6A1F8D !important; /* Purple header */
            color: white !important; /* White text for contrast */
            font-size: 1.2em !important; /* Larger font size for headers */
            font-weight: bold !important;
            padding: 15px 12px !important; /* More padding for larger header row */
            border: 1px solid #4a146e !important; /* Darker purple border */
            border-radius: 5px 5px 0 0; /* Rounded top corners if not full width */
        }
        /* Table Body Cells */
        .stDataFrame td {
            font-size: 0.95em !important;
            padding: 10px 12px !important;
            word-wrap: break-word; /* Ensure content wraps */
            white-space: normal; /* Override default Streamlit table nowrap */
        }
        /* Ensure the dataframe itself expands as wide as possible */
        div[data-testid="stDataFrame"] {
            width: 100% !important;
        }
        /* Hide dataframe internal scrollbar if not needed and handle content overflow for cells */
        .stDataFrame > div > div > div > div > div {
            overflow-x: hidden !important; 
        }

        /* Section Header for Instructions */
        .instructions-header {
            color: #6A1F8D;
            text-align: center;
            margin-top: 40px;
            margin-bottom: 20px;
            font-size: 2em;
        }
        .instructions-list {
            list-style-type: none; /* Remove default bullet points */
            padding-left: 0;
            margin-left: auto;
            margin-right: auto;
            max-width: 800px; /* Constrain width for readability */
        }
        .instructions-list li {
            background-color: #fce4ec; /* Lighter pink for list items */
            margin-bottom: 10px;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            line-height: 1.5;
            font-size: 1.05em;
            color: #444;
        }
        .instructions-list li strong {
            color: #6A1F8D; /* Emphasize keywords */
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
            Simply paste your list of URLs, and let the tool do the heavy lifting!
        </p>
    """, unsafe_allow_html=True)
    
    # --- URL INPUT AREA ---
    urls_input = st.text_area(
        "Enter URLs (one per line):", 
        height=180, # Slightly taller
        placeholder="https://example.com/topic-a-guide\nhttps://example.com/blog-post-on-topic-b\nhttps://example.com/service-page-c",
        key="url_input_area",
        help="Paste a list of full URLs (e.g., https://example.com/page)."
    )

    # --- BUTTONS ROW ---
    # Using a single column for the main button and then conditionally displaying others
    # This setup ensures 'Generate Links' is always there, and others appear after generation.
    main_button_col, download_csv_col, copy_to_sheets_col = st.columns([0.2, 0.2, 0.6]) # Adjust ratios

    # Generate Links Button (Pink - primary)
    if main_button_col.button("Generate Links", key="generate_btn", type="primary"):
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
            link_data = generate_links(urls)
            st.session_state['generated_links'] = link_data # Store in session state
            st.success(f"Success! Generated {len(link_data)} bidirectional link rows.")
            
    # --- RESULTS DISPLAY AND ADDITIONAL BUTTONS ---
    if 'generated_links' in st.session_state and st.session_state['generated_links']:
        st.markdown("<h3 style='color: #555; margin-top: 30px;'>Results:</h3>", unsafe_allow_html=True)
        
        # Display as a DataFrame
        df_display = pd.DataFrame(st.session_state['generated_links'])
        st.dataframe(df_display, hide_index=True, use_container_width=True)
        
        # CSV Download Button (Purple) - displayed next to Generate Links via column trickery or simply below results
        csv_data = convert_to_csv(st.session_state['generated_links'])
        
        # Place these buttons below the DataFrame now, as direct side-by-side with generate is tricky with Streamlit's state
        st.markdown("---") # Separator
        st.markdown("<h3 style='color: #555;'>Export Options:</h3>", unsafe_allow_html=True)
        
        export_col1, export_col2, _ = st.columns([0.2, 0.2, 0.6])

        export_col1.download_button(
            label="Download CSV Data",
            data=csv_data,
            file_name='internal_links_output.csv',
            mime='text/csv',
            key='download_csv_btn'
        )

        # Copy to Sheets Button (Light Blue)
        # This button uses JavaScript to copy. Streamlit's clipboard features are limited.
        csv_string_for_copy = convert_to_csv(st.session_state['generated_links']).decode('utf-8')
        
        # Inject JavaScript for copy-to-clipboard functionality
        st.markdown(f"""
        <button class="copy-to-sheets-btn" onclick="navigator.clipboard.writeText(`{csv_string_for_copy.replace('`', '\\`')}`)">
            Copy to Sheets (CSV)
        </button>
        <script>
            // Add a temporary status message after copying
            document.querySelector('.copy-to-sheets-btn').onclick = function() {{
                navigator.clipboard.writeText(`{csv_string_for_copy.replace('`', '\\`')}`).then(() => {{
                    const successDiv = document.createElement('div');
                    successDiv.innerHTML = '<div style="background-color: #d4edda; color: #155724; padding: 10px; border-radius: 8px; margin-top: 10px; font-size: 0.9em;">Data copied to clipboard! Paste into Google Sheets.</div>';
                    document.querySelector('.stDownloadButton').insertAdjacentElement('afterend', successDiv);
                    setTimeout(() => successDiv.remove(), 3000); // Remove after 3 seconds
                }}).catch(err => {{
                    alert('Could not copy text: ' + err);
                }});
            }};
        </script>
        """, unsafe_allow_html=True)


    # --- INSTRUCTIONS AT THE BOTTOM ---
    st.markdown("<hr style='border-top: 1px solid #ffabab; margin-top: 50px; margin-bottom: 30px;'>", unsafe_allow_html=True)
    st.markdown("<h2 class='instructions-header'>How to Use This Tool:</h2>", unsafe_allow_html=True)
    st.markdown(
        """
        <ul class='instructions-list'>
            <li><strong>Step 1: Prepare Your URLs</strong><br>
                Gather the complete list of URLs you want to interlink. Each URL must start with <code>http://</code> or <code>https://</code>.
                Example: <code>https://www.yourdomain.com/blog-post-1</code>
            </li>
            <li><strong>Step 2: Paste URLs</strong><br>
                Paste your list of URLs into the "Enter URLs" text box above. Place each URL on a new line.
            </li>
            <li><strong>Step 3: Generate Links</strong><br>
                Click the <span style='background-color: #ff69b4; color: white; padding: 3px 8px; border-radius: 5px; font-weight: bold;'>Generate Links</span> button. The tool will process your URLs and display all possible bidirectional internal linking pairs in a table.
            </li>
            <li><strong>Step 4: Review Results</strong><br>
                The table will show the <strong>Source URL</strong> (where the link goes), <strong>Target URL</strong> (where the link points to), a <strong>Suggested Anchor Text</strong>, and the full <strong>Link HTML</strong> code.
            </li>
            <li><strong>Step 5: Export Data</strong>
                <ul>
                    <li>Click the <span style='background-color: #9c27b0; color: white; padding: 3px 8px; border-radius: 5px; font-weight: bold;'>Download CSV Data</span> button to download a <code>.csv</code> file.</li>
                    <li>Click the <span style='background-color: #87CEEB; color: white; padding: 3px 8px; border-radius: 5px; font-weight: bold;'>Copy to Sheets (CSV)</span> button to copy the data directly to your clipboard, then simply paste it into Google Sheets or Excel.</li>
                </ul>
            </li>
            <li><strong>Step 6: Implement Links</strong><br>
                Use the generated data to implement internal links on your website. Remember to refine the "Suggested Anchor Text" with relevant keywords for optimal SEO.
            </li>
        </ul>
        """, unsafe_allow_html=True
    )

if __name__ == "__main__":
    app()
