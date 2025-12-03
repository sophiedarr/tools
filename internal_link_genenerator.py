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
    # Streamlit UI elements (using the requested color and emojis)
    st.markdown(f"""
        <h1 style='color: #6A1F8D; text-align: center;'>
            🔗 BIDIRECTIONAL INTERNAL LINK GENERATOR 🚀
        </h1>
        <p style='text-align: center;'>
            Paste your list of complete URLs below (one per line).
        </p>
    """, unsafe_allow_html=True)
    
    # 1. Input Area
    urls_input = st.text_area(
        "Enter URLs:", 
        height=150, 
        placeholder="https://example.com/page-1\nhttps://example.com/page-2\nhttps://example.com/page-3"
    )

    # 2. Process Button (using the pink color)
    if st.button("Generate Links", key="generate", help="Click to process the URLs", type="primary"):
        # Process and filter URLs
        urls = [
            url.strip() 
            for url in urls_input.split('\n') 
            if url.strip().startswith(('http://', 'https://'))
        ]

        if len(urls) < 2:
            st.error("Please enter at least two valid URLs (starting with http:// or https://) to generate links.")
            return

        # Generate data
        link_data = generate_links(urls)
        
        st.success(f"Success! Generated {len(link_data)} bidirectional link rows.")
        
        # 3. Display Results Table
        st.subheader("Generated Links")
        st.dataframe(link_data, hide_index=True, use_container_width=True)
        
        # 4. CSV Download Button (using the purple color)
        csv_data = convert_to_csv(link_data)
        
        st.download_button(
            label="Download CSV Data",
            data=csv_data,
            file_name='internal_links_output.csv',
            mime='text/csv',
            key='download-csv'
        )

if __name__ == "__main__":
    app()
