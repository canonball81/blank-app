import streamlit as st
import requests
import xml.etree.ElementTree as ET
import json
from urllib.parse import urlparse

st.set_page_config(page_title="Sitemap Parser for ML", layout="centered")
st.title("🔍 Sitemap Crawler & Exporter")

sitemap_url = st.text_input("Enter a sitemap.xml")

if st.button("Parse Sitemap"):
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()

        # Parse the XML
        root = ET.fromstring(response.content)
        namespace = {'ns': root.tag.split('}')[0].strip('{')}  # Extract the XML namespace

        urls = [elem.text for elem in root.findall('.//ns:loc', namespaces=namespace)]

        st.success(f"✅ Found {len(urls)} URLs")
        st.write(urls)

        # Extract structured data
        parsed_data = []
        for url in urls:
            parts = urlparse(url)
            parsed_data.append({
                "full_url": url,
                "domain": parts.netloc,
                "path": parts.path,
                "query": parts.query,
            })

        # Show JSON preview
        st.subheader("📦 Export Preview (JSON)")
        st.json(parsed_data[:10])

        # Download link
        json_file = json.dumps(parsed_data, indent=2)
        st.download_button("📥 Download JSON", json_file, file_name="sitemap_data.json", mime="application/json")

    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching sitemap: {e}")
    except ET.ParseError as e:
        st.error(f"Error parsing XML: {e}")
