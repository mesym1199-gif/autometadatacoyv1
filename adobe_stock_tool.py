import streamlit as st
import pandas as pd
import google.generativeai as genAI
from PIL import Image
import io
import base64

# Konfigurasi Halaman
st.set_page_config(page_title="Adobe Stock Metadata AI", page_icon="🎨", layout="wide")

st.title("🎨 Adobe Stock Metadata Tool")
st.markdown("""
Tool ini membantu Anda membuat **Title dan Keywords** otomatis menggunakan AI untuk Adobe Stock.
Upload gambar Anda, dapatkan metadata, dan download dalam format CSV.
""")

# Setup Sidebar untuk API Key
with st.sidebar:
    st.header("Konfigurasi")
    api_key = st.text_input("Masukan Gemini API Key:", type="password")
    st.info("Dapatkan API Key di [Google AI Studio](https://aistudio.google.com/)")

def generate_metadata(image_bytes, mime_type):
    if not api_key:
        st.error("Harap masukan API Key terlebih dahulu!")
        return None
    
    genAI.configure(api_key=api_key)
    model = genAI.GenerativeModel('gemini-1.5-flash')
    
    prompt = """
    Analyze this image and provide metadata for Adobe Stock.
    Return ONLY JSON:
    {
      "title": "Clear descriptive title (max 200 chars)",
      "keywords": "keyword1, keyword2, keyword3... (20-40 keywords)",
      "category": 0
    }
    """
    
    try:
        response = model.generate_content([
            prompt,
            {'mime_type': mime_type, 'data': image_bytes}
        ])
        # Bersihkan string dari markdown jika ada
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        import json
        return json.loads(clean_text)
    except Exception as e:
        st.error(f"Error AI: {e}")
        return None

# Upload File
uploaded_files = st.file_uploader("Upload Gambar (JPG, PNG, WEBP)", type=['jpg', 'jpeg', 'png', 'webp'], accept_multiple_files=True)

if uploaded_files:
    if 'results' not in st.session_state:
        st.session_state.results = []

    if st.button("🚀 Generate Metadata dengan AI"):
        progress_bar = st.progress(0)
        new_results = []
        
        for idx, uploaded_file in enumerate(uploaded_files):
            # Tampilkan gambar yang sedang diproses
            st.write(f"Memproses: {uploaded_file.name}")
            
            bytes_data = uploaded_file.getvalue()
            metadata = generate_metadata(bytes_data, uploaded_file.type)
            
            if metadata:
                new_results.append({
                    "Filename": uploaded_file.name,
                    "Title": metadata['title'],
                    "Keywords": metadata['keywords'],
                    "Category": metadata['category']
                })
            
            progress_bar.progress((idx + 1) / len(uploaded_files))
            
        st.session_state.results = new_results
        st.success("Selesai memproses!")

    # Tampilkan Tabel Hasil
    if st.session_state.results:
        df = pd.DataFrame(st.session_state.results)
        st.subheader("📋 Hasil Metadata")
        
        # Edit tabel secara langsung
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        
        # Download tombol
        csv = edited_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Adobe Stock CSV",
            data=csv,
            file_name='adobe_stock_metadata.csv',
            mime='text/csv',
        )

st.divider()
st.caption("Dibuat dengan ❤️ untuk Kontributor Adobe Stock")
