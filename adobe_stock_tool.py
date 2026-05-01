import streamlit as st
import pandas as pd
import google.generativeai as genai
from PIL import Image
import time
import json

# CONFIG

st.set_page_config(page_title="Adobe Stock AI Metadata", page_icon="🎨", layout="wide")

st.title("🚀 Adobe Stock Metadata AI (Stable Version)")
st.caption("No error • No infinite loading • Streamlit Cloud ready")

# SIDEBAR

with st.sidebar:
st.header("⚙️ Konfigurasi")
api_key = st.text_input("Masukan Gemini API Key:", type="password")

# FUNCTION (FIXED)

def generate_metadata(uploaded_file):
try:
if not api_key:
return None

````
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    image = Image.open(uploaded_file)

    prompt = """
    Analyze this image for Adobe Stock.

    Return ONLY JSON:
    {
      "title": "Clear descriptive title (max 200 chars)",
      "keywords": "keyword1, keyword2, keyword3... (20-40 keywords)",
      "category": 0
    }
    """

    response = model.generate_content(
        [prompt, image],
        request_options={"timeout": 20}
    )

    text = response.text.replace('```json', '').replace('```', '').strip()

    try:
        data = json.loads(text)
    except:
        data = {
            "title": text[:100],
            "keywords": "",
            "category": 0
        }

    return data

except Exception as e:
    return {
        "title": "Error",
        "keywords": str(e),
        "category": 0
    }
````

# UPLOAD

uploaded_files = st.file_uploader(
"Upload Gambar",
type=["jpg", "jpeg", "png", "webp"],
accept_multiple_files=True
)

# PROCESS

if uploaded_files:
if st.button("🚀 Generate Metadata"):
if not api_key:
st.error("Masukkan API Key dulu!")
else:
results = []
progress = st.progress(0)
status = st.empty()

```
        for i, file in enumerate(uploaded_files):
            status.info(f"Processing: {file.name}")

            metadata = generate_metadata(file)

            if metadata:
                results.append({
                    "Filename": file.name,
                    "Title": metadata.get("title", ""),
                    "Keywords": metadata.get("keywords", ""),
                    "Category": metadata.get("category", 0)
                })

            progress.progress((i + 1) / len(uploaded_files))
            time.sleep(1)  # anti rate limit

        st.success("✅ Selesai!")

        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "📥 Download CSV",
            csv,
            "adobe_stock_metadata.csv",
            "text/csv"
        )
```
