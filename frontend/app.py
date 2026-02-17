"""Streamlit Frontend for Langextract POC"""
import streamlit as st
import requests
import base64

# Page configuration
st.set_page_config(
    page_title="Langextract POC",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Custom CSS - Clean and minimal
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Clean header */
    .main-header {
        font-size: 2.5rem;
        font-weight: 600;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    /* Metrics styling */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 600;
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: 600;
        padding: 0.6rem 1.5rem;
        border-radius: 0.5rem;
        border: none;
        font-size: 1rem;
    }
    .stButton>button:hover {
        background-color: #155a8a;
        border: none;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        padding: 1rem;
        border: 2px dashed #1f77b4;
        border-radius: 0.5rem;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 1rem;
        font-weight: 500;
    }
    
    /* Reduce padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)


def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def analyze_document(uploaded_file):
    """Send document to API for analysis"""
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
    
    with st.spinner("🔍 Analyzing document... This may take 5-10 seconds"):
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/analyze",
                files=files,
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json(), None
            else:
                error_detail = response.json().get("detail", "Unknown error")
                return None, f"Error {response.status_code}: {error_detail}"
        except requests.exceptions.Timeout:
            return None, "Request timed out. Please try again."
        except Exception as e:
            return None, f"Error: {str(e)}"


def download_pdf_report(job_id):
    """Download PDF report from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/report/{job_id}")
        if response.status_code == 200:
            return response.content
        return None
    except:
        return None


def display_pdf(pdf_bytes):
    """Display PDF in iframe"""
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


def main():
    # Header
    st.markdown('<div class="main-header">📄 Langextract POC</div>', unsafe_allow_html=True)
    
    # Check API health
    if not check_api_health():
        st.error("⚠️ Backend not running. Start with: `python run.py`")
        st.stop()
    
    # Main content
    if 'show_results' not in st.session_state:
        st.session_state.show_results = False
    
    if not st.session_state.show_results:
        # Upload screen - centered
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("<h3 style='text-align: center;'>Upload your document to get started</h3>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(
                "Drag and drop or browse",
                type=["pdf", "docx", "txt"],
                label_visibility="collapsed"
            )
            
            if uploaded_file:
                st.success(f"✓ {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
                
                if st.button("Analyze Document", type="primary", use_container_width=True):
                    result, error = analyze_document(uploaded_file)
                    
                    if error:
                        st.error(error)
                    else:
                        st.session_state.result = result
                        st.session_state.show_results = True
                        st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #666;'>Supports: PDF, DOCX, TXT • Max size: 10MB</p>", unsafe_allow_html=True)
    
    else:
        # Results screen
        result = st.session_state.result
        
        # Top bar with metrics and reset button
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
        
        with col1:
            st.metric("Type", result['document_type'].upper())
        
        with col2:
            st.metric("Confidence", f"{result['confidence'] * 100:.0f}%")
        
        with col3:
            st.metric("Entities", result['extraction_count'])
        
        with col4:
            if st.button("↻", help="Analyze another document"):
                st.session_state.show_results = False
                st.session_state.result = None
                st.rerun()
        
        st.divider()
        
        # Tabs
        tab1, tab2 = st.tabs(["📄 Report", "📊 Data"])
        
        with tab1:
            # PDF viewer
            pdf_bytes = download_pdf_report(result['job_id'])
            
            if pdf_bytes:
                display_pdf(pdf_bytes)
                
                # Download button below PDF
                st.download_button(
                    label="Download PDF",
                    data=pdf_bytes,
                    file_name=f"report_{result['job_id']}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.error("Failed to load report")
        
        with tab2:
            # Entities grouped by category
            if result['extractions']:
                grouped = {}
                for ext in result['extractions']:
                    cls = ext['extraction_class']
                    if cls not in grouped:
                        grouped[cls] = []
                    grouped[cls].append(ext)
                
                for cls, items in grouped.items():
                    with st.expander(f"{cls.replace('_', ' ').title()} ({len(items)})", expanded=False):
                        for item in items:
                            mention = item['attributes'].get('mention_count', 0)
                            if mention > 1:
                                st.markdown(f"**{item['extraction_text']}** _(×{mention})_")
                            else:
                                st.markdown(f"**{item['extraction_text']}**")
                            
                            # Show key attributes only
                            if item['attributes']:
                                attrs = [f"{k}: {v}" for k, v in item['attributes'].items() 
                                        if k != 'mention_count' and v]
                                if attrs:
                                    st.caption(" • ".join(attrs[:3]))  # Max 3 attributes
            else:
                st.info("No entities extracted")
            
            st.divider()
            
            # Download JSONL
            try:
                jsonl_response = requests.get(f"{API_BASE_URL}/api/v1/data/{result['job_id']}")
                if jsonl_response.status_code == 200:
                    st.download_button(
                        label="Download JSONL Data",
                        data=jsonl_response.content,
                        file_name=f"data_{result['job_id']}.jsonl",
                        mime="application/jsonl",
                        use_container_width=True
                    )
            except:
                pass


if __name__ == "__main__":
    main()
