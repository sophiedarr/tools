import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from urllib.parse import urljoin
import xml.etree.ElementTree as ET

# Page Config
st.set_page_config(page_title="Internal Link Optimiser", page_icon="✨", layout="wide")

# Custom Styling for Colors, Sidebar Width, and Info Boxes
st.markdown(f"""
    <style>
    /* Main background color */
    .stApp {{
        background-color: #FFC7D5;
    }}
    
    /* Sidebar background color and width */
    [data-testid="stSidebar"] {{
        background-color: #FFE6EC;
        min-width: 400px !important;
        max-width: 400px !important;
    }}

    /* "Run Audit 🌸" Button Styling */
    div.stButton > button:first-child {{
        background-color: #ff4b4b;
        color: white;
        border-radius: 10px;
        height: 3em;
        width: 100%;
        font-weight: bold;
        border: none;
    }}

    /* Make Info boxes white */
    .stAlert {{
        background-color: white !important;
        color: black !important;
        border: 1px solid #FFE6EC;
    }}
    </style>
    """, unsafe_allow_html=True)

st.title("✨ Internal Link Optimiser ✨")
st.write("Clean up your internal link structure by identifying 301s and 404s inside your page content.")

# --- SIDEBAR INPUTS ---
with st.sidebar:
    st.header("1. Input Settings")
    mode = st.radio("Select Audit Mode", ["Single URL", "Bulk URL List", "Sitemap (XML)"])
    
    if mode == "Single URL":
        input_data = st.text_input("Enter Page URL", placeholder="https://example.com/page")
    elif mode == "Bulk URL List":
        input_data = st.text_area("Paste URLs (one per line)", placeholder="https://example.com/page1\nhttps://example.com/page2", height=300)
    else:
        input_data = st.text_input("Enter Sitemap URL", placeholder="https://example.com/sitemap.xml")
    
    st.header("2. Crawl Controls")
    slow_mode = st.checkbox("Slow Mode (Safe Crawling)", value=True)
    st.info("Slow Mode (0.2s delay) helps prevent your IP from being blocked by the website's firewall.")

# --- CORE LOGIC FUNCTIONS ---
def get_urls_from_sitemap(sitemap_url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(sitemap_url, headers=headers, timeout=10)
        root = ET.fromstring(response.content)
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        return [loc.text for loc in root.findall('.//ns:loc', namespace)]
    except Exception as e:
        st.error(f"Sitemap Error: {e}")
        return []

def audit_page_links(source_url):
    results = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        resp = requests.get(source_url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        main_content = soup.find('main') or soup.find('article') or soup.find('div', id='MainContent') or soup.find('body')
        links = main_content.find_all('a', href=True)
        
        for link in links:
            original_href = link['href']
            anchor = link.get_text(strip=True) or "[Image/No Text]"
            absolute_link = urljoin(source_url, original_href)

            if not absolute_link.startswith('http'): continue

            try:
                link_check = requests.get(absolute_link, headers=headers, timeout=10, allow_redirects=True)
                
                if len(link_check.history) > 0:
                    initial_status = link_check.history[0].status_code
                    final_url = link_check.url
                else:
                    initial_status = link_check.status_code
                    final_url = "Direct"

                if initial_status != 200:
                    results.append({
                        "Source Page": source_url,
                        "Anchor Text": anchor,
                        "Link in Body": absolute_link,
                        "Status Code": initial_status,
                        "Final Destination": final_url
                    })
            except:
                results.append({
                    "Source Page": source_url, "Anchor Text": anchor, 
                    "Link in Body": absolute_link, "Status Code": "Error/Timeout", "Final Destination": "N/A"
                })
            
            if slow_mode: time.sleep(0.2)
        return results
    except Exception as e:
        return []

# --- RUN AUDIT ---
if st.button("Run Audit 🌸"):
    urls_to_crawl = []
    
    if mode == "Single URL" and input_data:
        urls_to_crawl = [input_data.strip()]
    elif mode == "Bulk URL List" and input_data:
        urls_to_crawl = [line.strip() for line in input_data.split('\n') if line.strip()]
    elif mode == "Sitemap (XML)" and input_data:
        urls_to_crawl = get_urls_from_sitemap(input_data.strip())

    if urls_to_crawl:
        all_issues = []
        progress_bar = st.progress(0)
        status_text = st.empty()

        for idx, url in enumerate(urls_to_crawl):
            status_text.text(f"Scanning {idx+1}/{len(urls_to_crawl)}: {url}")
            page_issues = audit_page_links(url)
            all_issues.extend(page_issues)
            progress_bar.progress((idx + 1) / len(urls_to_crawl))
        
        status_text.text("✅ Audit Complete!")
        
        if all_issues:
            df = pd.DataFrame(all_issues)
            st.subheader("Findings (Redirects & Broken Links)")
            st.dataframe(df, use_container_width=True)
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Results (CSV)", csv, "audit_results.csv", "text/csv")
        else:
            st.balloons()
            st.success("Great news! No 301s or 404s found in the body text of these pages.")
    else:
        st.warning("Please provide a valid URL or list of URLs.")
