import streamlit as st
import pandas as pd
import google.generativeai as genai
from PIL import Image
import io
import concurrent.futures

# Konfigurasi Halaman
st.set_page_config(page_title="Adobe Stock AI Metadata", page_icon="🎨", layout="wide")

st.title("🚀 Adobe Stock Metadata AI (Turbo)")
st.markdown("""
Aplikasi ini menggunakan **Gemini AI** untuk generate Title & Keywords secara paralel. 
Jauh lebih cepat untuk proses banyak gambar sekaligus.
""")

# Setup Sidebar
with st.sidebar:
    st.header("⚙️ Konfigurasi")
    api_key = st.text_input("Masukan Gemini API Key:", type="password")
    st.info("Dapatkan API Key [di sini](https://aistudio.google.com/)")
    st.divider()
    st.caption("v2.0 - Parallel Processing Enabled")

def process_single_image(uploaded_file):
    """Fungsi untuk memproses satu gambar via API"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash') # Model tercepat
        
        bytes_data = uploaded_file.getvalue()
        
        prompt = """
        Analyze this image for Adobe Stock.
        Respond ONLY in JSON format:
        {
          "title": "Clear descriptive title (max 200 chars)",
          "keywords": "keyword1, keyword2, keyword3... (20-40 keywords)",
          "category": 0
        }
        """
        
        response = model.generate_content([
            prompt,
            {'mime_type': uploaded_file.type, 'data': bytes_data}
        ])
        
        import json
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(clean_text)
        
        return {
            "Filename": uploaded_file.name,
            "Title": data.get('title', ''),
            "Keywords": data.get('keywords', ''),
            "Category": data.get('category', 0)
        }
    except Exception as e:
        return {"Filename": uploaded_file.name, "Title": "Error", "Keywords": str(e), "Category": 0}

# Upload File
uploaded_files = st.file_uploader("Upload Gambar", type=['jpg', 'jpeg', 'png', 'webp'], accept_multiple_files=True)

if uploaded_files:
    if st.button("⚡ Generate Metadata (Serverless Parallel)"):
        if not api_key:
            st.error("Masukkan API Key di sidebar!")
        else:
            results = []
            progress_text = "Memproses gambar secara paralel..."
            progress_bar = st.progress(0)
            
            # Gunakan ThreadPoolExecutor untuk kecepatan maksimal
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                # Map fungsi ke semua file
                future_to_file = {executor.submit(process_single_image, f): f for f in uploaded_files}
                
                completed = 0
                for future in concurrent.futures.as_completed(future_to_file):
                    result = future.result()
                    results.append(result)
                    completed += 1
                    progress_bar.progress(completed / len(uploaded_files))
            
            st.session_state.results = results
            st.success(f"Berhasil memproses {len(results)} gambar!")

    # Tampilkan Tabel
    if 'results' in st.session_state and st.session_state.results:
        df = pd.DataFrame(st.session_state.results)
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        
        csv = edited_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV untuk Adobe Stock",
            data=csv,
            file_name='adobe_metadata.csv',
            mime='text/csv',
        )
