import streamlit as st
from streamlit_folium import folium_static
import tempfile
import os
import base64
import time
import json

# Frontend components for embedding Google Maps JS
import streamlit.components.v1 as components

# Import our custom modules
from pdf_extractor import PDFExtractor
from xml_converter import XMLConverter
from geo_mapper import GeoMapper
from address_parser import AddressParser
from google_geocoder import geocode_structured

# Set page configuration
st.set_page_config(
    page_title="E-Fatura Analiz",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern Professional UI CSS with TailwindCSS principles
def load_modern_ui_css():
    st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Modern Professional Theme Variables - Dark Theme (elegant) */
    :root {
        --bg-primary: #0B0F17;        /* page background */
        --bg-card: #111827;           /* card background */
        --bg-card-hover: #142033;     /* hover state */
        --bg-accent: #0F172A;         /* subtle surfaces */
        --bg-button: #3B82F6;         /* primary button */
        --bg-button-hover: #2563EB;   /* primary hover */
        --bg-button-secondary: #1D4ED8;
        --bg-button-secondary-hover: #1E40AF;
        --text-primary: #F9FAFB;      /* titles */
        --text-secondary: #E5E7EB;    /* content */
        --text-muted: #9CA3AF;        /* subdued */
        --text-white: #FFFFFF;
        --border-light: #1F2A44;      /* soft borders */
        --border-medium: #2A3A5F;
        --border-accent: #60A5FA;     /* accents */
        --shadow-sm: 0 1px 2px 0 rgba(0,0,0,0.25);
        --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.35), 0 2px 4px -1px rgba(0,0,0,0.3);
        --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.45), 0 4px 6px -2px rgba(0,0,0,0.4);
        --shadow-xl: 0 20px 25px -5px rgba(0,0,0,0.55), 0 10px 10px -5px rgba(0,0,0,0.5);
        --radius-sm: 0.375rem;
        --radius-md: 0.5rem;
        --radius-lg: 0.75rem;
        --radius-xl: 1rem;
        --radius-2xl: 1.5rem;
        --spacing-xs: 0.5rem;
        --spacing-sm: 0.75rem;
        --spacing-md: 1rem;
        --spacing-lg: 1.5rem;
        --spacing-xl: 2rem;
        --spacing-2xl: 3rem;
    }
    
    /* Global styling */
    .main {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: var(--bg-primary);
        min-height: 100vh;
        padding: var(--spacing-xl) 0;
        color: var(--text-primary);
        line-height: 1.6;
    }
    
    /* Unified centered container */
    .block-container {
        background: var(--bg-primary);
        padding: 0;
        margin: 0 auto;
        max-width: 1200px;
    }
    
    /* Visible, styled sidebar */
    [data-testid="stSidebar"] {
        display: block !important;
        background: var(--bg-card) !important;
        border-right: 1px solid var(--border-light) !important;
    }
    
    /* Global text styling */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
        font-weight: 700;
        margin-bottom: var(--spacing-md);
        line-height: 1.3;
    }
    
    h1 { font-size: 2.5rem; font-weight: 800; }
    h2 { font-size: 2rem; font-weight: 700; }
    h3 { font-size: 1.5rem; font-weight: 600; }
    h4 { font-size: 1.25rem; font-weight: 600; }
    
    p, span, div {
        color: var(--text-secondary) !important;
    }
    
    /* Modern Card System */
    .modern-card {
        background: var(--bg-primary);
        border-radius: var(--radius-2xl);
        box-shadow: var(--shadow-lg);
        border: 1px solid var(--border-light);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        overflow: hidden;
    }
    
    .modern-card:hover {
        box-shadow: var(--shadow-xl);
        transform: translateY(-2px);
        border-color: var(--border-medium);
        background: var(--bg-primary);
    }
    
    .modern-card-header {
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-primary) 100%);
        padding: var(--spacing-xl) var(--spacing-xl) var(--spacing-lg);
        border-bottom: 1px solid var(--border-light);
    }
    
    .modern-card-body {
        padding: var(--spacing-xl);
    }
    
    .modern-card-footer {
        background: var(--bg-primary);
        padding: var(--spacing-lg) var(--spacing-xl);
        border-top: 1px solid var(--border-light);
    }
    
    /* Header styling */
    .app-header {
        text-align: center;
        margin-bottom: var(--spacing-2xl);
    }
    
    .app-header h1 {
        background: linear-gradient(135deg, var(--text-primary) 0%, var(--text-secondary) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: var(--spacing-sm);
    }
    
    .app-header p {
        color: var(--text-muted) !important;
        font-size: 1.1rem;
        font-weight: 500;
    }
    
    /* Upload section */
    .upload-section {
        background: var(--bg-primary);
        border-radius: var(--radius-2xl);
        box-shadow: var(--shadow-lg);
        border: 2px dashed var(--border-accent);
        padding: var(--spacing-2xl);
        text-align: center;
        margin-bottom: var(--spacing-2xl);
        transition: all 0.3s ease;
    }
    
    .upload-section:hover {
        border-color: var(--bg-button);
        background: var(--bg-primary);
        transform: translateY(-2px);
        box-shadow: var(--shadow-xl);
    }
    
    /* Company info cards */
    .company-card {
        background: var(--bg-primary);
        border-radius: var(--radius-xl);
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-light);
        padding: var(--spacing-xl);
        height: 100%;
        transition: all 0.3s ease;
    }
    
    .company-card:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-2px);
        background: var(--bg-primary);
    }
    
    .company-card-header {
        display: flex;
        align-items: center;
        gap: var(--spacing-sm);
        margin-bottom: var(--spacing-lg);
        padding-bottom: var(--spacing-md);
        border-bottom: 2px solid var(--border-accent);
    }
    
    .company-card-header h4 {
        color: var(--text-primary) !important;
        margin: 0;
        font-weight: 600;
    }
    
    .company-info-item {
        display: flex;
        align-items: flex-start;
        gap: var(--spacing-sm);
        margin-bottom: var(--spacing-md);
        padding: var(--spacing-sm);
        background: var(--bg-accent);
        border-radius: var(--radius-md);
        border-left: 3px solid var(--border-accent);
    }
    
    .company-info-item:last-child {
        margin-bottom: 0;
    }
    
    .company-info-icon {
        color: var(--border-accent);
        font-size: 1.1rem;
        margin-top: 2px;
        flex-shrink: 0;
    }
    
    .company-info-content {
        flex: 1;
    }
    
    .company-info-label {
        font-weight: 600;
        color: var(--text-primary) !important;
        font-size: 0.9rem;
        margin-bottom: 2px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .company-info-value {
        color: var(--text-secondary) !important;
        font-size: 1rem;
        line-height: 1.5;
    }
    
    /* Modern data table */
    .modern-table {
        background: var(--bg-card);
        border-radius: var(--radius-xl);
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-light);
        overflow: hidden;
        margin: var(--spacing-lg) 0;
    }
    
    .modern-table-header {
        background: linear-gradient(135deg, var(--text-primary) 0%, var(--text-secondary) 100%);
        color: var(--bg-card) !important;
        padding: var(--spacing-lg) var(--spacing-xl);
        font-weight: 600;
        font-size: 1.1rem;
        display: flex;
        align-items: center;
        gap: var(--spacing-sm);
    }
    
    /* Button styling */
    .stButton > button {
        background: var(--bg-button);
        border: none;
        border-radius: var(--radius-lg);
        color: var(--text-white) !important;
        font-weight: 600;
        padding: var(--spacing-md) var(--spacing-xl);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        font-family: 'Inter', sans-serif;
        box-shadow: var(--shadow-md);
        font-size: 1rem;
    }
    
    .stButton > button:hover {
        background: var(--bg-button-hover);
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Secondary button */
    .btn-secondary {
        background: var(--bg-button-secondary) !important;
    }
    
    .btn-secondary:hover {
        background: var(--bg-button-secondary-hover) !important;
    }
    
    /* File uploader styling */
    .stFileUploader {
        background: transparent !important;
    }
    
    .stFileUploader > div {
        background: transparent !important;
    }
    
    /* Progress bars */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, var(--bg-button) 0%, var(--bg-button-secondary) 100%);
        border-radius: var(--radius-md);
    }
    
    /* Metrics */
    [data-testid="metric-container"] {
        background: var(--bg-primary);
        border: 1px solid var(--border-light);
        padding: var(--spacing-lg);
        border-radius: var(--radius-xl);
        box-shadow: var(--shadow-md);
        transition: all 0.3s ease;
        text-align: center;
    }
    
    [data-testid="metric-container"]:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-2px);
        border-color: var(--border-accent);
        background: var(--bg-primary);
    }
    
    [data-testid="metric-container"] label {
        color: var(--text-muted) !important;
        font-weight: 600;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    [data-testid="metric-container"] div[data-testid="metric-value"] {
        color: var(--text-primary) !important;
        font-size: 1.5rem;
        font-weight: 700;
        margin-top: var(--spacing-sm);
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background: var(--bg-accent);
        border-radius: var(--radius-lg);
        border: 1px solid var(--border-light);
        font-weight: 600;
        color: var(--text-primary) !important;
        transition: all 0.3s ease;
        padding: var(--spacing-md) var(--spacing-lg);
    }
    
    .streamlit-expanderHeader:hover {
        background: var(--bg-card);
        border-color: var(--border-accent);
        transform: translateY(-1px);
    }
    
    /* Map container */
    .map-container {
        border-radius: var(--radius-2xl);
        overflow: hidden;
        box-shadow: var(--shadow-lg);
        margin: var(--spacing-lg) 0;
        border: 1px solid var(--border-light);
        background: var(--bg-card);
    }
    
    /* Google Maps button */
    .gmaps-button {
        display: inline-block;
        width: 100%;
        text-align: center;
        text-decoration: none;
        background: var(--bg-button-secondary);
        border: none;
        border-radius: var(--radius-lg);
        color: var(--text-white) !important;
        font-weight: 600;
        padding: var(--spacing-md) var(--spacing-xl);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        font-family: 'Inter', sans-serif;
        box-shadow: var(--shadow-md);
        margin-top: var(--spacing-lg);
        font-size: 1rem;
    }
    
    .gmaps-button:hover {
        background: var(--bg-button-secondary-hover);
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
        color: var(--text-white) !important;
        text-decoration: none;
    }
    
    /* Success/Info/Warning styling */
    .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: var(--radius-lg);
        border: none;
        box-shadow: var(--shadow-md);
        padding: var(--spacing-md) var(--spacing-lg);
    }
    
    /* Dataframe styling */
    .stDataFrame {
        background: var(--bg-primary);
        border-radius: var(--radius-xl);
        padding: var(--spacing-lg);
        border: 1px solid var(--border-light);
        box-shadow: var(--shadow-md);
    }
    
    /* Code blocks */
    .stCodeBlock {
        background: var(--bg-primary);
        border-radius: var(--radius-lg);
        border: 1px solid var(--border-light);
    }
    
    /* Section dividers */
    .section-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, var(--border-light) 20%, var(--border-light) 80%, transparent 100%);
        margin: var(--spacing-xl) 0;
        border: none;
    }
    
    /* Financial summary cards */
    .financial-card {
        background: var(--bg-primary);
        border-radius: var(--radius-xl);
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-light);
        padding: var(--spacing-lg);
        text-align: center;
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .financial-card:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-2px);
        border-color: var(--border-accent);
        background: var(--bg-primary);
    }
    
    .financial-icon {
        font-size: 2rem;
        margin-bottom: var(--spacing-sm);
        color: var(--border-accent);
    }
    
    .financial-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-primary) !important;
        margin-bottom: var(--spacing-xs);
    }
    
    .financial-label {
        color: var(--text-muted) !important;
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .block-container { 
            padding: var(--spacing-md); 
            max-width: 100%;
        }
        .modern-card-body { 
            padding: var(--spacing-lg); 
        }
        .modern-card-header { 
            padding: var(--spacing-lg); 
        }
        .company-card { 
            padding: var(--spacing-lg); 
        }
        .upload-section { 
            padding: var(--spacing-xl); 
        }
    }
    /* Sidebar inner spacing */
    [data-testid="stSidebar"] .block-container { padding: 1rem 0.75rem; }

    /* Dividers */
    hr, .section-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, var(--border-light) 20%, var(--border-light) 80%, transparent 100%);
        border: none;
        margin: var(--spacing-lg) 0;
    }

</style>
""", unsafe_allow_html=True)

# Light theme overrides to switch from dark palette to modern light SaaS look
def load_light_ui_overrides():
    st.markdown(
        """
        <style>
        :root {
            --bg-primary: #F5F7FA;
            --bg-card: #FFFFFF;
            --bg-card-hover: #F7FAFF;
            --bg-accent: #F3F6FB;
            --bg-button: #4F9DDE;
            --bg-button-hover: #3E8DCE;
            --bg-button-secondary: #1D72B8;
            --bg-button-secondary-hover: #155E98;
            --text-primary: #1F2937;
            --text-secondary: #374151;
            --text-muted: #6B7280;
            --text-white: #FFFFFF;
            --border-light: #E6EAF0;
            --border-medium: #D3DAE6;
            --border-accent: #A8C7F0;
        }

        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
            background: var(--bg-primary) !important;
            color: var(--text-primary) !important;
            font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, 'Helvetica Neue', Arial;
        }

        /* Make sure the sidebar remains visible (the base CSS hides it) */
        [data-testid="stSidebar"] {
            display: block !important;
            background: var(--bg-card) !important;
            border-right: 1px solid var(--border-light) !important;
        }

        /* Cards */
        .modern-card, .company-card, .financial-card, .map-container, .stDataFrame, [data-testid="metric-container"] {
            background: var(--bg-card) !important;
            border: 1px solid var(--border-light) !important;
            box-shadow: 0 8px 24px rgba(16,24,40,0.06) !important;
        }

        /* Headings and text colors */
        h1, h2, h3, h4, h5, h6 { color: var(--text-primary) !important; }
        p, span, div { color: var(--text-secondary) !important; }

        /* Buttons */
        .stButton > button { background: var(--bg-button) !important; color: #fff !important; }
        .stButton > button:hover { background: var(--bg-button-hover) !important; }

        /* Upload section style to light */
        .upload-section { background: #f0f6ff !important; border-color: var(--border-accent) !important; }

        /* Tables */
        .stDataFrame { background: var(--bg-card) !important; }
        
        /* Compact container max-width */
        .block-container { max-width: 1200px; margin: 0 auto; }
        </style>
        """,
        unsafe_allow_html=True,
    )

def main():
    # Load cohesive dark theme CSS
    load_modern_ui_css()
    
    # Sidebar collapse state
    if 'sidebar_collapsed' not in st.session_state:
        st.session_state.sidebar_collapsed = False
    
    # Top-left minimal toggle button
    c_tgl, c_rest = st.columns([0.1, 0.9])
    with c_tgl:
        if st.button("☰", key="toggle_sidebar_btn", help="Menüyü Göster/Gizle", use_container_width=True):
            st.session_state.sidebar_collapsed = not st.session_state.sidebar_collapsed
    
    # Inject collapse CSS when active
    if st.session_state.sidebar_collapsed:
        st.markdown(
            """
            <style>
            /* Collapse sidebar to icons-only */
            [data-testid="stSidebar"] { width: 64px !important; min-width: 64px !important; }
            [data-testid="stSidebar"] .block-container { padding: 0.5rem 0.35rem !important; }
            [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
            [data-testid="stSidebar"] h4, [data-testid="stSidebar"] p, [data-testid="stSidebar"] .stMarkdown,
            [data-testid="stSidebar"] [data-testid="metric-container"],
            [data-testid="stSidebar"] .st-expander, [data-testid="stSidebar"] hr { display: none !important; }
            
            /* Buttons show only first character (emoji) */
            [data-testid="stSidebar"] .stButton > button { width: 48px; height: 44px; padding: 0; text-align: center; }
            [data-testid="stSidebar"] .stButton > button { font-size: 0 !important; }
            [data-testid="stSidebar"] .stButton > button::first-letter { font-size: 1.25rem; }
            
            /* Smooth transition */
            [data-testid="stSidebar"] { transition: width 0.25s ease, min-width 0.25s ease; }
            </style>
            """,
            unsafe_allow_html=True,
        )
    
    # Modern top navbar
    st.markdown(
        """
        <div class="nav-bar" style="
            background: var(--bg-card);
            border: 1px solid var(--border-light);
            border-radius: 16px;
            padding: 14px 20px; 
            display: flex; align-items: center; justify-content: space-between;
            box-shadow: 0 8px 24px rgba(16,24,40,0.06);
            margin-bottom: 16px;
        ">
          <div class="nav-left" style="display:flex;align-items:center;gap:12px;">
            <div class="nav-logo" style="width:28px;height:28px;border-radius:8px;background: linear-gradient(135deg, #4F9DDE, #A8E6CF);"></div>
            <div>
              <div class="nav-title" style="font-weight:700;letter-spacing:.2px;color:var(--text-primary)">E‑Fatura Analiz Merkezi</div>
              <div class="nav-subtle" style="color:var(--text-muted);font-size:12px;">PDF'leri analiz edin, XML'e dönüştürün ve adresleri harita üzerinde görüntüleyin</div>
            </div>
          </div>
          <div class="nav-right" style="color:var(--text-muted);font-size:12px;">v1.0 • Modern UI</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Sidebar with advanced features (kept but compact); can be removed later if not needed
    with st.sidebar:
        st.markdown("### 🚀 Platform Özellikleri")
        
        features = [
            {"icon": "📋", "title": "Akıllı PDF Çıkarma", "desc": "Yapay zeka destekli metin analizi", "key": "pdf_extraction"},
            {"icon": "🏢", "title": "Kurumsal Bilgiler", "desc": "Satıcı ve alıcı detayları", "key": "company_info"},
            {"icon": "💰", "title": "Finansal Analiz", "desc": "KDV ve toplam hesaplamaları", "key": "financial_analysis"},
            {"icon": "🗺️", "title": "Coğrafi Haritalama", "desc": "İnteraktif adres gösterimi", "key": "geo_mapping"},
            {"icon": "📄", "title": "XML Dönüştürme", "desc": "UBL-TR standart formatı", "key": "xml_conversion"}
        ]
        
        # Initialize feature states
        if 'selected_features' not in st.session_state:
            st.session_state.selected_features = set()
        
        for i, feature in enumerate(features):
            # Create interactive feature cards
            feature_key = f"feature_{feature['key']}"
            
            # Check if feature is selected
            is_selected = feature['key'] in st.session_state.selected_features
            selected_class = "feature-selected" if is_selected else ""
            
            # Create clickable container
            container = st.container()
            with container:
                if st.button(
                    f"{feature['icon']} {feature['title']}", 
                    key=feature_key,
                    help=feature['desc'],
                    use_container_width=True
                ):
                    # Toggle feature selection
                    if feature['key'] in st.session_state.selected_features:
                        st.session_state.selected_features.remove(feature['key'])
                        st.toast(f"❌ {feature['title']} deaktif edildi", icon="🔧")
                    else:
                        st.session_state.selected_features.add(feature['key'])
                        st.toast(f"✅ {feature['title']} aktif edildi", icon="🚀")
                
                # Show feature description
                if is_selected:
                    st.success(f"✅ {feature['desc']}")
                else:
                    st.info(f"ℹ️ {feature['desc']}")
            
            st.markdown("---")
        
        st.markdown("---")
        
        # Statistics
        st.markdown("### 📊 Canlı İstatistikler")
        if 'processed_invoices' not in st.session_state:
            st.session_state.processed_invoices = 0
        if 'total_amount_processed' not in st.session_state:
            st.session_state.total_amount_processed = 0
            
        col1, col2 = st.columns(2)
        with col1:
            st.metric("İşlenen Fatura", st.session_state.processed_invoices)
        with col2:
            st.metric("Toplam Tutar", f"₺{st.session_state.total_amount_processed:,.0f}")
        
        st.markdown("---")
        
        # Quick tips
        st.markdown("### 💡 Hızlı İpuçları")
        st.markdown("""
        • **Yüksek Kalite**: En iyi sonuçlar için 300 DPI PDF kullanın
        • **Desteklenen Format**: Türkiye GİB e-fatura standardı
        • **Güvenlik**: Dosyalarınız işlem sonrası otomatik silinir
        • **Hız**: Ortalama işlem süresi 10-30 saniye
        """)
    
    # Left panel collapse state and dynamic two-column layout
    if 'left_collapsed' not in st.session_state:
        st.session_state.left_collapsed = False

    # Smooth width transition for columns
    st.markdown(
        """
        <style>
        /* Animate column width changes */
        [data-testid="stHorizontalBlock"] > div {
            transition: flex-basis 0.25s ease, width 0.25s ease, max-width 0.25s ease;
        }
        .left-panel-toggle button { padding: 0.35rem 0.5rem; font-size: 0.9rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    left_ratio, right_ratio = ([0.12, 0.88] if st.session_state.left_collapsed else [1, 2])
    left_col, right_col = st.columns([left_ratio, right_ratio], gap="large")
    with left_col:
        # Toggle at top of left panel
        tcol1, tcol2 = st.columns([1, 6])
        with tcol1:
            label = "▶" if st.session_state.left_collapsed else "◀"
            if st.button(label, key="left_panel_toggle", help="Paneli daralt/genişlet", use_container_width=True):
                st.session_state.left_collapsed = not st.session_state.left_collapsed
                st.rerun()
        with tcol2:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        
        if not st.session_state.left_collapsed:
            st.markdown(
                """
                <div class="modern-card">
                  <div class="modern-card-header">
                    <h3 style="margin:0">📁 Fatura Yükleme</h3>
                  </div>
                  <div class="modern-card-body">
                """,
                unsafe_allow_html=True,
                
            )
            uploaded_file = st.file_uploader(
                "PDF dosyasını seçin veya sürükleyip bırakın",
                type=["pdf", "jpg", "jpeg", "png"],
                help="Maksimum dosya boyutu: 25MB",
                label_visibility="collapsed"
            )
            st.markdown("</div></div>", unsafe_allow_html=True)
        else:
            uploaded_file = None if 'uploaded_placeholder' not in st.session_state else None
    
    if uploaded_file is not None:
        # Update statistics
        st.session_state.processed_invoices += 1
        
        # Compact file info
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("📝 Dosya", uploaded_file.name.replace('.pdf', ''))
        with c2:
            st.metric("📋 Format", uploaded_file.type.upper())
        with c3:
            st.metric("📊 Boyut", f"{uploaded_file.size / 1024:.1f} KB")
        
        st.markdown("---")
        
        # Save the uploaded file temporarily
        # Dosya uzantısını al
        file_ext = os.path.splitext(uploaded_file.name)[-1].lower()
        if file_ext not in [".pdf", ".jpg", ".jpeg", ".png"]:
            st.error("Sadece PDF veya resim dosyası yükleyebilirsiniz.")
            return

        # Geçici dosyayı uygun uzantı ile kaydet
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            pdf_path = tmp_file.name
        
        try:
            # Advanced progress tracking
            progress_container = st.container()
            with progress_container:
                st.markdown("### ⚙️ İşlem Durumu")
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Step 1: Reading PDF
                status_text.markdown('<p class="status-warning">📄 PDF dosyası okunuyor...</p>', unsafe_allow_html=True)
                progress_bar.progress(20)
                time.sleep(0.5)
                
                # Extract data from PDF
                pdf_extractor = PDFExtractor(pdf_path)
                invoice_data = pdf_extractor.extract_invoice_data()
                
                # Step 2: Analyzing data
                status_text.markdown('<p class="status-warning">🔍 Veriler analiz ediliyor...</p>', unsafe_allow_html=True)
                progress_bar.progress(50)
                time.sleep(0.5)
                
                # Debug (hidden by default)
                with st.expander("🔍 Debug: Çıkarılan Veriler", expanded=False):
                    st.json(invoice_data, expanded=False)
                
                if not invoice_data.get('invoice_number'):
                    status_text.markdown('<p class="status-error">❌ PDF\'den fatura bilgileri çıkarılamadı!</p>', unsafe_allow_html=True)
                    st.error("Lütfen geçerli bir e-fatura PDF'si yüklediğinizden emin olun.")
                    st.info("Debug: Çıkarılan veri yapısını yukardaki 'Debug' bölümünden kontrol edebilirsiniz.")
                    return
                
                # Step 3: Processing XML
                status_text.markdown('<p class="status-warning">📄 XML formatına dönüştürülüyor...</p>', unsafe_allow_html=True)
                progress_bar.progress(80)
                
                # Convert to XML
                xml_converter = XMLConverter(invoice_data)
                xml_content = xml_converter.convert_to_ubl_tr()
                
                # Debug: XML preview (hidden)
                with st.expander("🔍 XML Çıktısı Önizlemesi (Debug)", expanded=False):
                    # Show first few lines of XML for debugging
                    xml_lines = xml_content.split('\n')
                    preview_lines = xml_lines[:50]  # First 50 lines
                    st.code('\n'.join(preview_lines), language="xml")
                    
                    # Validate line items specifically
                    if invoice_data.get('line_items'):
                        st.markdown("**Line Items Kontrolü:**")
                        for i, item in enumerate(invoice_data['line_items'], 1):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.text(f"Item {i} Description:")
                                st.code(item.get('description', 'N/A'))
                            with col2:
                                st.text(f"Item {i} Unit Price:")
                                st.code(item.get('unit_price', 'N/A'))
                            with col3:
                                st.text(f"Item {i} Amount:")
                                st.code(item.get('amount', 'N/A'))
                
                # Update total amount processed
                try:
                    total_amount = float(invoice_data.get('total_amount', '0').replace(',', '').replace('₺', ''))
                    st.session_state.total_amount_processed += total_amount
                except:
                    pass
                
                # Step 4: Complete
                status_text.markdown('<p class="status-success">✅ İşlem başarıyla tamamlandı!</p>', unsafe_allow_html=True)
                progress_bar.progress(100)
                time.sleep(1)
                
                # Clear progress
                progress_container.empty()
            
            # Display results message
            st.success("🎉 Fatura başarıyla analiz edildi!")

            # Left: XML actions (modern card), only when panel is expanded
            if not st.session_state.left_collapsed:
                with left_col:
                    st.markdown(
                        """
                        <div class="modern-card">
                          <div class="modern-card-header">
                            <h3 style="margin:0">📄 XML</h3>
                          </div>
                          <div class="modern-card-body">
                        """,
                        unsafe_allow_html=True,
                    )
                    st.download_button(
                        label="📥 XML'i İndir",
                        data=xml_content,
                        file_name=f"fatura_{invoice_data.get('invoice_number', 'output')}.xml",
                        mime="application/xml",
                        use_container_width=True,
                        type="primary"
                    )
                    with st.expander("📄 XML Önizleme", expanded=False):
                        st.code(xml_content, language="xml", line_numbers=False)
                    st.markdown("</div></div>", unsafe_allow_html=True)

            # Right: Map Section
            with right_col:
                vendor_address = invoice_data.get('vendor_address', '')
                customer_address = invoice_data.get('customer_address', '')

                if vendor_address or customer_address:
                    st.markdown(
                        """
                        <div class="modern-card">
                          <div class="modern-card-header">
                            <h3 style="margin:0">🗺️ Harita</h3>
                          </div>
                          <div class="modern-card-body">
                        """,
                        unsafe_allow_html=True,
                    )

                    with st.spinner('📍 Adresler coğrafi koordinatlara dönüştürülüyor...'):
                        parser = AddressParser()
                        geocoding_key = st.secrets.get("GOOGLE_GEOCODING_API_KEY", "")
                        maps_js_key = st.secrets.get("GOOGLE_MAPS_JS_API_KEY", "")

                    if not geocoding_key or not maps_js_key:
                        st.warning("Google Maps anahtarları tanımlı değil. Lütfen secrets dosyanıza GOOGLE_GEOCODING_API_KEY ve GOOGLE_MAPS_JS_API_KEY ekleyin.")
                    else:
                        markers = []

                        if vendor_address:
                            with st.expander("Seller Address Debug Details", expanded=False):
                                st.info(f"**1. Ham Adres:**\n```\n{vendor_address}\n```")
                                v_comp = parser.parse(vendor_address)
                                st.info(f"**2. Ayrıştırılmış Bileşenler:**\n```json\n{json.dumps(v_comp, indent=2, ensure_ascii=False)}\n```")
                                vendor_name = invoice_data.get('vendor_name')
                                st.info(f"**3. Ham Firma Adı:**\n```\n{vendor_name or ''}\n```")
                                st.info("**4. Geocoding Stratejisi:**\n- Google Geocoding (ad+adres+components)\n- Google Places Text Search (ad+adres)\n- Google Places (sadece ad)\n- Google Places (ad + şehir)\n- Google Places (sadece adres)")
                                v_geo = geocode_structured(v_comp, geocoding_key, org_name=vendor_name)
                                if v_geo and v_geo.get('query'):
                                    st.info(f"**5. Son Sorgu (Ad + Adres):**\n```\n{v_geo.get('query')}\n```")
                                if v_geo and v_geo.get('api_used'):
                                    st.info(f"**6. Kullanılan API:** {v_geo.get('api_used')}")
                                st.info(f"**7. Coğrafi Kodlama Sonucu:**\n```json\n{json.dumps(v_geo, indent=2, ensure_ascii=False) if v_geo else 'None'}\n```")
                                if v_geo:
                                    markers.append({
                                        "label": f"Satıcı: {invoice_data.get('vendor_name','')}",
                                        "address": v_geo.get("formatted_address"),
                                        "lat": v_geo["lat"],
                                        "lng": v_geo["lng"],
                                        "is_perfect": v_geo.get("is_perfect", False),
                                        "confidence": v_geo.get("confidence", 0.0),
                                        "strategy": v_geo.get("strategy"),
                                        "api_used": v_geo.get("api_used"),
                                        "type": "vendor",
                                    })
                                else:
                                    st.warning("Satıcı adresi için koordinat bulunamadı.")

                        if customer_address:
                            c_comp = parser.parse(customer_address)
                            customer_name = invoice_data.get('customer_name')
                            with st.expander("Buyer Address Debug Details", expanded=False):
                                st.info(f"**1. Ham Adres:**\n```\n{customer_address}\n```")
                                st.info(f"**2. Ayrıştırılmış Bileşenler:**\n```json\n{json.dumps(c_comp, indent=2, ensure_ascii=False)}\n```")
                                st.info(f"**3. Ham Firma Adı:**\n```\n{customer_name or ''}\n```")
                                st.info("**4. Geocoding Stratejisi:**\n- Google Geocoding (ad+adres+components)\n- Google Places Text Search (ad+adres)\n- Google Places (sadece ad)\n- Google Places (ad + şehir)\n- Google Places (sadece adres)")
                                c_geo = geocode_structured(c_comp, geocoding_key, org_name=customer_name)
                                if c_geo and c_geo.get('query'):
                                    st.info(f"**5. Son Sorgu (Ad + Adres):**\n```\n{c_geo.get('query')}\n```")
                                if c_geo and c_geo.get('api_used'):
                                    st.info(f"**6. Kullanılan API:** {c_geo.get('api_used')}")
                                st.info(f"**7. Coğrafi Kodlama Sonucu:**\n```json\n{json.dumps(c_geo, indent=2, ensure_ascii=False) if c_geo else 'None'}\n```")
                                if c_geo:
                                    markers.append({
                                        "label": f"Müşteri: {invoice_data.get('customer_name','')}",
                                        "address": c_geo.get("formatted_address"),
                                        "lat": c_geo["lat"],
                                        "lng": c_geo["lng"],
                                        "is_perfect": c_geo.get("is_perfect", False),
                                        "confidence": c_geo.get("confidence", 0.0),
                                        "strategy": c_geo.get("strategy"),
                                        "api_used": c_geo.get("api_used"),
                                        "type": "customer",
                                    })
                                else:
                                    st.warning("Müşteri adresi için koordinat bulunamadı.")

                        if markers:
                            markers_json = json.dumps(markers)
                            # The entire map logic is now self-contained in this HTML block.
                            # It handles markers, info windows, route drawing, and auto-fitting bounds.
                            map_html = f"""
                            <div id="map" style="width:100%;height:500px;border-radius:12px;"></div>
                            <script>
                            // Ensure this function is globally accessible for the Google Maps callback.
                            window.initMap = function() {{
                              const markersData = {markers_json};
                              if (!markersData || markersData.length === 0) return;

                              const map = new google.maps.Map(document.getElementById('map'), {{
                                mapTypeControl: false,
                                streetViewControl: false,
                                fullscreenControl: false
                              }});

                              const bounds = new google.maps.LatLngBounds();
                              let sellerPosition = null;
                              let buyerPosition = null;

                              markersData.forEach(m => {{
                                const isSeller = m.type === 'vendor';
                                const position = {{ lat: m.lat, lng: m.lng }};
                                
                                const marker = new google.maps.Marker({{
                                  position: position,
                                  map: map,
                                  title: m.label,
                                  label: isSeller ? 'S' : 'B',
                                }});

                                const infoHtml = `<strong>${{m.label}}</strong>` +
                                  `<br>${{m.address || 'Adres detayı yok'}}` +
                                  (m.confidence ? `<br>Güven: ${{m.is_perfect ? 'Kesin' : m.confidence.toFixed(2)}}` : '') +
                                  (m.strategy ? `<br>Strateji: ${{m.strategy}}` : '') +
                                  (m.api_used ? `<br>API: ${{m.api_used}}` : '');
                                const infoWindow = new google.maps.InfoWindow({{
                                  content: infoHtml
                                }});
                                marker.addListener('click', () => infoWindow.open(map, marker));
                                
                                bounds.extend(position);

                                if (isSeller) sellerPosition = position;
                                else buyerPosition = position;
                              }});

                              // Draw route if both seller and buyer are present
                              if (sellerPosition && buyerPosition) {{
                                const directionsService = new google.maps.DirectionsService();
                                const directionsRenderer = new google.maps.DirectionsRenderer({{
                                    suppressMarkers: true, // We use our custom markers
                                    preserveViewport: true // Don't auto-zoom here, we do it manually
                                }});
                                directionsRenderer.setMap(map);

                                directionsService.route({{
                                  origin: sellerPosition,
                                  destination: buyerPosition,
                                  travelMode: google.maps.TravelMode.DRIVING
                                }}, (response, status) => {{
                                  if (status === 'OK') {{
                                    directionsRenderer.setDirections(response);
                                    // Extend the bounds to include the entire route
                                    const routeBounds = response.routes[0].bounds;
                                    bounds.union(routeBounds);
                                    map.fitBounds(bounds, 50); // 50px padding
                                  }} else {{
                                    console.warn('Directions request failed due to ' + status);
                                    // Fallback to fitting bounds to markers if routing fails
                                    map.fitBounds(bounds, 50);
                                  }}
                                }});
                              }} else {{
                                // If only one marker, or no route to draw, just fit to markers
                                map.fitBounds(bounds, 50);
                              }}
                            }};
                            </script>
                            <script async defer src="https://maps.googleapis.com/maps/api/js?key={maps_js_key}&callback=initMap&language=tr&region=TR"></script>
                            """
                            components.html(map_html, height=520)
                            # Conditionally render an external Google Maps directions link styled as a button
                            try:
                                seller = next((m for m in markers if m.get("type") == "vendor"), None)
                                buyer = next((m for m in markers if m.get("type") == "customer"), None)
                                if (
                                    seller and buyer and
                                    ("lat" in seller and "lng" in seller) and
                                    ("lat" in buyer and "lng" in buyer)
                                ):
                                    gmaps_url = f"https://www.google.com/maps/dir/{seller['lat']},{seller['lng']}/{buyer['lat']},{buyer['lng']}"
                                    st.markdown(
                                        f"""
                                        <div style="margin-top: 0.5rem;">
                                          <a href="{gmaps_url}" target="_blank" rel="noopener noreferrer"
                                             style="
                                               display: inline-block; width: 100%; text-align: center; text-decoration: none;
                                               background: var(--bg-card); border: 1px solid var(--border-color);
                                               border-radius: 10px; color: var(--text-primary) !important; font-weight: 600;
                                               padding: 0.6rem 1rem; transition: all 0.2s ease; font-family: 'Inter', sans-serif;
                                               box-shadow: var(--shadow-sm);
                                              ">
                                            🧭 Google Haritalarda Aç
                                          </a>
                                        </div>
                                        """,
                                        unsafe_allow_html=True,
                                    )
                            except Exception:
                                # Fail silently if any unexpected structure occurs
                                pass
                        else:
                            st.warning("⚠️ Harita oluşturulamadı. Adres bilgileri eksik veya hatalı olabilir.")
                else:
                    st.info("📍 Harita gösterimi için adres bilgisi bulunamadı.")
                # Close map card if opened
                if vendor_address or customer_address:
                    st.markdown("</div></div>", unsafe_allow_html=True)

            # Optional: Detailed invoice data below two-column section
            display_invoice_data(invoice_data)
            
        except Exception as e:
            st.error(f"PDF işlenirken hata oluştu: {str(e)}")
            st.error("Hata detayları:")
            st.exception(e)
        
        finally:
            # Clean up the temporary file
            try:
                os.unlink(pdf_path)
            except:
                pass
    
    # Modern footer section
    st.markdown("---")
    st.markdown("### ℹ️ Platform Hakkında")
    
    # Create footer with three columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🚀 Teknoloji**
        - Yapay Zeka Destekli OCR
        - Python & Streamlit
        - Folium Haritalama
        - UBL-TR XML Standardı
        """)
    
    with col2:
        st.markdown("""
        **📊 Özellikler**
        - Hızlı PDF Analizi
        - Otomatik Veri Çıkarma
        - Coğrafi Kodlama
        - Gerçek Zamanlı İşlem
        """)
    
    with col3:
        st.markdown("""
        **🔒 Güvenlik**
        - Dosya Otomatik Silme
        - Yerel İşlem
        - Veri Gizliliği
        - SSL Güvenlik
        """)
    
    # Enhanced about section
    with st.expander("📚 Detaylı Bilgi", expanded=False):
        st.markdown("""
        ## 🎯 E-Fatura PDF Analiz Merkezi
        
        Bu platform, Türkiye'deki e-fatura PDF'lerini analiz etmek için geliştirilmiş 
        gelişmiş bir yapay zeka destekli sistemdir.
        
        ### 🔧 Ana İşlevler:
        
        **1. 📋 Akıllı PDF Çıkarma**
        - OCR teknolojisi ile metin tanıma
        - Yapısal veri analizi
        - Çoklu format desteği
        
        **2. 🏢 Kurumsal Bilgi İşleme**
        - Satıcı/alıcı firma bilgileri
        - Vergi kimlik numarası tespiti
        - Adres standardizasyonu
        
        **3. 💰 Finansal Analiz**
        - KDV hesaplamaları
        - Tevkifat tespiti
        - Toplam doğrulama
        
        **4. 🗺️ Coğrafi Haritalama**
        - Adres geocoding
        - İnteraktif harita
        - Mesafe hesaplama
        
        **5. 📄 XML Dönüştürme**
        - UBL-TR standardı
        - Yapısal XML çıktı
        - İndirilebilir format
        
        ### 📈 Desteklenen Formatlar:
        - GİB E-Fatura PDF
        - Özel Sektör E-Fatura
        - Ticari Faturalar
        
        ### 🔒 Gizlilik ve Güvenlik:
        - Tüm dosyalar işlem sonrası otomatik silinir
        - Veriler sunucuda saklanmaz
        - Yerel işlem önceliği
        - SSL şifreli bağlantı
        
        ---
        
        **⚡ Performans:** Ortalama işlem süresi 10-30 saniye  
        **🎯 Doğruluk:** %95+ veri çıkarma başarısı  
        **🌍 Dil:** Türkçe ve İngilizce destekli  
        """)
    
    # Footer credits
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 1rem;'>
            <p>💻 E-Fatura PDF Analiz Merkezi | 🚀 Powered by AI & Python</p>
            <p style='font-size: 0.8rem;'>© 2024 - Gelişmiş PDF Analiz Sistemi</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

def display_invoice_data(invoice_data):
    """Display the extracted invoice data with modern design"""
    
    st.markdown("### 📋 Fatura Detayları")
    
    # Header information with modern cards
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="📄 Fatura Numarası",
            value=invoice_data.get('invoice_number', 'Bulunamadı'),
            help="Sistemde kayıtlı fatura numarası"
        )
    with col2:
        st.metric(
            label="📅 Fatura Tarihi",
            value=invoice_data.get('invoice_date', 'Bulunamadı'),
            help="Faturanın düzenlenme tarihi"
        )
    
    st.markdown("---")
    
    # Company information in modern cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-card vendor-card">
            <h4>🏢 Satıcı Firma Bilgileri</h4>
        </div>
        """, unsafe_allow_html=True)
        
        vendor_name = invoice_data.get('vendor_name', 'Bulunamadı')
        vendor_tax = invoice_data.get('vendor_tax_id', 'Bulunamadı')
        vendor_addr = invoice_data.get('vendor_address', 'Bulunamadı')
        
        st.markdown(f"""
        **👤 Firma Unvanı:**  
        {vendor_name}
        
        **🆔 Vergi Kimlik No:**  
        {vendor_tax}
        
        **📍 Adres:**  
        {vendor_addr}
        """)
    
    with col2:
        st.markdown("""
        <div class="info-card customer-card">
            <h4>🏪 Alıcı Firma Bilgileri</h4>
        </div>
        """, unsafe_allow_html=True)
        
        customer_name = invoice_data.get('customer_name', 'Bulunamadı')
        customer_tax = invoice_data.get('customer_tax_id', 'Bulunamadı')
        customer_addr = invoice_data.get('customer_address', 'Bulunamadı')
        
        st.markdown(f"""
        **👤 Firma Unvanı:**  
        {customer_name}
        
        **🆔 Vergi Kimlik No:**  
        {customer_tax}
        
        **📍 Adres:**  
        {customer_addr}
        """)
    
    st.markdown("---")
    
    # Line Items with modern design
    st.markdown("### 🛍️ Fatura Kalemleri")
    
    if invoice_data.get('line_items'):
        # Create enhanced table
        import pandas as pd
        
        # Prepare data with better formatting
        data = []
        for i, item in enumerate(invoice_data['line_items'], 1):
            data.append({
                "#": i,
                "📝 Açıklama": item.get('description', 'Bulunamadı'),
                "📊 Miktar": f"{item.get('quantity', 'N/A')} {item.get('unit', '')}",
                "💰 Birim Fiyat": f"₺{item.get('unit_price', 'N/A')}",
                "📈 KDV": f"%{item.get('tax_rate', 'N/A')}",
                "💵 Tutar": f"₺{item.get('amount', 'N/A')}"
            })
        
        df = pd.DataFrame(data)
        
        # Display styled dataframe
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "#": st.column_config.NumberColumn("Sıra", width="small"),
                "📝 Açıklama": st.column_config.TextColumn("Açıklama", width="large"),
                "📊 Miktar": st.column_config.TextColumn("Miktar", width="small"),
                "💰 Birim Fiyat": st.column_config.TextColumn("Birim Fiyat", width="small"),
                "📈 KDV": st.column_config.TextColumn("KDV Oranı", width="small"),
                "💵 Tutar": st.column_config.TextColumn("Tutar", width="small"),
            }
        )
        
        # Summary for line items
        total_items = len(invoice_data['line_items'])
        st.info(f"📦 Toplam {total_items} kalem bulundu")
        
    else:
        st.warning("📦 Faturada kalem bilgisi bulunamadı")
    
    st.markdown("---")
    
    # Financial summary with enhanced metrics
    st.markdown("### 💰 Finansal Özet")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        subtotal = invoice_data.get('subtotal', '0')
        st.metric(
            label="💵 Ara Toplam",
            value=f"₺{subtotal}",
            help="KDV hariç toplam tutar"
        )
    
    with col2:
        tax_amount = invoice_data.get('tax_amount', '0')
        st.metric(
            label="📊 KDV Tutarı",
            value=f"₺{tax_amount}",
            help="Toplam KDV tutarı"
        )
    
    with col3:
        total_amount = invoice_data.get('total_amount', '0')
        st.metric(
            label="💳 Genel Toplam",
            value=f"₺{total_amount}",
            help="KDV dahil toplam tutar"
        )
    
    with col4:
        # Calculate effective tax rate if possible
        try:
            subtotal_num = float(subtotal.replace(',', '').replace('₺', ''))
            tax_num = float(tax_amount.replace(',', '').replace('₺', ''))
            if subtotal_num > 0:
                tax_rate = (tax_num / subtotal_num) * 100
                st.metric(
                    label="📈 Ort. KDV Oranı",
                    value=f"%{tax_rate:.1f}",
                    help="Ortalama KDV oranı"
                )
            else:
                st.metric("📈 Ort. KDV Oranı", "N/A")
        except:
            st.metric("📈 Ort. KDV Oranı", "N/A")
    
    # Additional information
    if invoice_data.get('withholding_tax'):
        st.warning(f"⚠️ **Tevkifat Tutarı:** ₺{invoice_data.get('withholding_tax')}")
    
    if invoice_data.get('notes'):
        st.markdown("### 📝 Ek Notlar")
        st.info(invoice_data['notes'])
    
    # Quality indicator
    quality_score = 0
    total_checks = 5
    
    if invoice_data.get('invoice_number'): quality_score += 1
    if invoice_data.get('invoice_date'): quality_score += 1
    if invoice_data.get('vendor_name'): quality_score += 1
    if invoice_data.get('customer_name'): quality_score += 1
    if invoice_data.get('total_amount'): quality_score += 1
    
    quality_percentage = (quality_score / total_checks) * 100
    
    if quality_percentage >= 80:
        st.success(f"✅ **Veri Kalitesi:** %{quality_percentage:.0f} - Mükemmel")
    elif quality_percentage >= 60:
        st.warning(f"⚠️ **Veri Kalitesi:** %{quality_percentage:.0f} - İyi")
    else:
        st.error(f"❌ **Veri Kalitesi:** %{quality_percentage:.0f} - Düşük")

if __name__ == "__main__":
    main()
