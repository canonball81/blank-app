import streamlit as st
import requests
import xml.etree.ElementTree as ET
import json
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import time

st.set_page_config(page_title="Sitemap Parser for ML", layout="centered")
st.title("🔍 Sitemap Crawler & Content Exporter")

sitemap_url = st.text_input("Enter a sitemap.xml URL:")

if st.button("Parse and Fetch Content"):
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()

        # Parse the XML
        root = ET.fromstring(response.content)
        namespace = {'ns': root.tag.split('}')[0].strip('{')}  # Extract the XML namespace

        urls = [elem.text for elem in root.findall('.//ns:loc', namespaces=namespace)]

        st.success(f"✅ Found {len(urls)} URLs")

        parsed_data = []
        progress = st.progress(0)

        for idx, url in enumerate(urls):
            try:
                page = requests.get(url, timeout=10)
                soup = BeautifulSoup(page.content, 'html.parser')

                title = soup.title.string.strip() if soup.title else ""
                body_text = ' '.join(p.get_text(strip=True) for p in soup.find_all('p'))

                parsed_data.append({
                    "full_url": url,
                    "title": title,
                    "text": body_text
                })

            except Exception as e:
                parsed_data.append({
                    "full_url": url,
                    "error": str(e)
                })

            progress.progress((idx + 1) / len(urls))
            time.sleep(0.5)  # be polite with delay

        # Preview
        st.subheader("📦 Export Preview (First 3 Pages)")
        st.json(parsed_data[:3])

        # Download
        json_file = json.dumps(parsed_data, indent=2)
        st.download_button("📥 Download JSON", json_file, file_name="sitemap_page_content.json", mime="application/json")

    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching sitemap: {e}")
    except ET.ParseError as e:
        st.error(f"Error parsing XML: {e}")
