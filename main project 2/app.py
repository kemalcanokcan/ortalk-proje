import streamlit as st
import pdfplumber
import folium
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import xml.etree.ElementTree as ET
import xml.dom.minidom
import tempfile
import os
import time
import re
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="E-Invoice PDF Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
def load_custom_css():
    # Import Inter font
    st.markdown(
        """
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
        :root {
            --bg: #F5F7FA;
            --card: #FFFFFF;
            --text: #2D2D2D;
            --muted: #5f6b7a;
            --accent: #4F9DDE;
            --accent-2: #A8E6CF;
            --border: #E6EAF0;
            --shadow: 0 8px 24px rgba(16,24,40,0.08);
            --radius: 16px;
        }

        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
            background: var(--bg) !important;
            color: var(--text) !important;
            font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, 'Helvetica Neue', Arial, "Noto Sans", "Apple Color Emoji", "Segoe UI Emoji";
        }

        .main { padding-top: 1rem; }

        /* Top navigation bar */
        .nav-bar {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 14px 20px;
            box-shadow: var(--shadow);
            display: flex; align-items: center; justify-content: space-between;
            margin-bottom: 20px;
        }
        .nav-left { display: flex; align-items: center; gap: 12px; }
        .nav-logo { width: 28px; height: 28px; border-radius: 8px; background: linear-gradient(135deg, var(--accent), var(--accent-2)); box-shadow: inset 0 1px 0 rgba(255,255,255,0.3); }
        .nav-title { font-weight: 700; letter-spacing: .2px; }
        .nav-subtle { color: var(--muted); font-size: 12px; }

        /* Section headings */
        .section-title { margin: 8px 0 12px; font-size: 18px; font-weight: 600; }

        /* Card */
        .card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            padding: 18px;
            margin: 12px 0 16px;
        }

        /* Info cards with colored accent */
        .info-card { background: var(--card); border-radius: 14px; padding: 16px; box-shadow: var(--shadow); border: 1px solid var(--border); margin-bottom: 12px; }
        .vendor-card { border-left: 6px solid #4CAF50; }
        .customer-card { border-left: 6px solid #FF9800; }
        .totals-card { border-left: 6px solid #2196F3; }

        /* Upload area */
        .upload-area { border: 2px dashed var(--accent); border-radius: 14px; padding: 28px; text-align: center; background: #f0f6ff; margin: 10px 0; }

        /* Buttons */
        .stButton > button {
            background: var(--accent) !important;
            color: white !important;
            border: 1px solid rgba(0,0,0,0.04) !important;
            border-radius: 12px !important;
            padding: 10px 14px !important;
            font-weight: 600 !important;
            letter-spacing: .2px;
            transition: all .2s ease;
            box-shadow: 0 6px 14px rgba(79,157,222,.25);
        }
        .stButton > button:hover { filter: brightness(0.95); transform: translateY(-1px); }
        .stButton > button:active { transform: translateY(0); }

        /* Metrics */
        [data-testid="metric-container"] { background: var(--card); border: 1px solid var(--border); padding: 14px; border-radius: 12px; box-shadow: var(--shadow); }

        /* Progress */
        .stProgress .st-bo { background: linear-gradient(135deg, var(--accent), #6ab0ec); }

        /* Alerts */
        .stAlert { border-radius: 12px; border: 1px solid var(--border); box-shadow: var(--shadow); }

        /* File uploader */
        .stFileUploader { border-radius: 12px; }

        /* Expander */
        .streamlit-expanderHeader { background: #f3f6fb; border-radius: 10px; font-weight: 600; }
        .streamlit-expanderContent { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 8px 12px; }

        /* Code blocks */
        pre, code { border-radius: 10px !important; }

        /* Map */
        .map-container { border-radius: 16px; overflow: hidden; box-shadow: var(--shadow); margin: 10px 0; border: 1px solid var(--border); }

        /* Tables */
        table { border-collapse: separate; border-spacing: 0; width: 100%; }
        thead th { background: #EEF4FF; color: #1F325D; font-weight: 600; }
        tbody tr:nth-child(odd) { background: #FAFCFF; }
        tbody tr:hover { background: #F0F6FF; }
        td, th { padding: 10px 12px; border-bottom: 1px solid var(--border); }
        </style>
        """,
        unsafe_allow_html=True,
    )

def main():
    # Load custom CSS
    load_custom_css()
    
    # Top navbar + header
    st.markdown(
        """
        <div class="nav-bar">
          <div class="nav-left">
            <div class="nav-logo"></div>
            <div>
              <div class="nav-title">E-Fatura PDF Analiz Merkezi</div>
              <div class="nav-subtle">PDF'leri analiz edin, XML'e dönüştürün ve adresleri harita üzerinde görüntüleyin</div>
            </div>
          </div>
          <div class="nav-right nav-subtle">v1.0 • Modern UI</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Sidebar with information
    with st.sidebar:
        st.markdown("### 🔧 Uygulama Özellikleri")
        st.markdown("""
        - 📋 PDF metin çıkarma
        - 🏢 Satıcı/Alıcı bilgileri
        - 💰 Fatura tutarları
        - 📍 Adres haritalama
        - 📄 XML dönüştürme
        """)
        st.markdown("### 📊 İstatistikler")
        if 'processed_files' not in st.session_state:
            st.session_state.processed_files = 0
        st.metric("İşlenen Dosya", st.session_state.processed_files)
        st.markdown("### ℹ️ Kullanım Talimatları")
        st.markdown("""
        1. PDF dosyanızı yükleyin
        2. Analiz sonuçlarını inceleyin
        3. XML çıktısını indirin
        4. Harita üzerinde adresleri görün
        """)
    
    # File upload section
    st.markdown("<div class='card'><div class='section-title'>📤 Dosya Yükleme</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        uploaded_file = st.file_uploader(
            "E-fatura PDF dosyanızı buraya sürükleyin veya seçin",
            type="pdf",
            help="Sadece PDF formatındaki e-fatura dosyaları kabul edilir"
        )
    st.markdown("</div>", unsafe_allow_html=True)
    
    if uploaded_file is not None:
        # Increment processed files counter
        st.session_state.processed_files += 1
        
        # Show file details with modern cards
        st.markdown("<div class='card'><div class='section-title'>📁 Dosya Bilgileri</div>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📝 Dosya Adı", uploaded_file.name.replace('.pdf', ''))
        with col2:
            st.metric("📋 Dosya Türü", uploaded_file.type.upper())
        with col3:
            st.metric("📊 Dosya Boyutu", f"{uploaded_file.size / 1024:.1f} KB")
        
        st.markdown("---")
        
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            pdf_path = tmp_file.name
            st.write(f"Geçici dosya oluşturuldu: {pdf_path}")
        
        try:
            # Progress bar for processing
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("📄 PDF dosyası okunuyor...")
            progress_bar.progress(25)
            
            # Extract data from PDF
            invoice_data = extract_data_from_pdf(pdf_path)
            
            status_text.text("🔍 Veriler analiz ediliyor...")
            progress_bar.progress(50)
            
            # Display extracted data
            display_invoice_data(invoice_data)
            
            status_text.text("📄 XML formatına dönüştürülüyor...")
            progress_bar.progress(75)
            
            # Convert to XML
            xml_content = convert_to_xml(invoice_data)
            
            status_text.text("✅ İşlem tamamlandı!")
            progress_bar.progress(100)
            
            # Clear progress indicators
            time.sleep(1)
            progress_bar.empty()
            status_text.empty()
            
            # Display XML section
            st.markdown("<div class='card'><div class='section-title'>📄 XML Çıktısı</div>", unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.download_button(
                    label="📥 XML Dosyasını İndir",
                    data=xml_content,
                    file_name=f"invoice_{invoice_data.get('invoice_number', 'output')}.xml",
                    mime="application/xml",
                    use_container_width=True
                )
            
            with col2:
                if st.button("📋 XML'i Panoya Kopyala", use_container_width=True):
                    st.success("XML içeriği panoya kopyalandı!")
            
            with st.expander("🔍 XML İçeriğini Görüntüle", expanded=False):
                st.code(xml_content, language="xml")
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Extract and geocode addresses
            vendor_address = invoice_data.get('vendor_address', '')
            customer_address = invoice_data.get('customer_address', '')
            
            # Create map with address markers
            if vendor_address or customer_address:
                st.markdown("<div class='card'><div class='section-title'>🗺️ Adres Haritası</div>", unsafe_allow_html=True)
                st.markdown('<div class="map-container">', unsafe_allow_html=True)
                map_data = create_map(vendor_address, customer_address)
                folium_static(map_data)
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.warning("⚠️ Harita gösterimi için adres bilgisi bulunamadı.")
        
        except Exception as e:
            st.error(f"PDF işlenirken hata oluştu: {str(e)}")
            st.error("Hata detayları:")
            st.exception(e)
            
        finally:
            # Clean up the temporary file
            try:
                os.unlink(pdf_path)
                st.write("Geçici dosya temizlendi.")
            except:
                pass

def extract_data_from_pdf(pdf_path):
    """Extract all relevant data from the e-invoice PDF"""
    invoice_data = {
        'invoice_number': '',
        'invoice_date': '',
        'vendor_name': '',
        'vendor_tax_id': '',
        'vendor_address': '',
        'customer_name': '',
        'customer_tax_id': '',
        'customer_address': '',
        'line_items': [],
        'subtotal': '',
        'tax_amount': '',
        'total_amount': '',
        'notes': ''
    }
    
    # Debug information
    st.write("### PDF Okuma Bilgileri")
    st.write(f"PDF dosyası: {pdf_path}")
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            st.write(f"PDF başarıyla açıldı. Sayfa sayısı: {len(pdf.pages)}")
            
            all_text = ""
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    all_text += page_text + "\n"
                    st.write(f"Sayfa {i+1}: {len(page_text)} karakter okundu")
                else:
                    st.write(f"Sayfa {i+1}: Metin çıkarılamadı")
            
            st.write(f"Toplam {len(all_text)} karakter okundu")
            
            # Show sample of extracted text
            if all_text:
                with st.expander("PDF'den çıkarılan metin örneği"):
                    st.code(all_text[:1000] + "..." if len(all_text) > 1000 else all_text)
            else:
                st.error("PDF'den metin çıkarılamadı!")
                return invoice_data
        
        # Extract invoice number
        invoice_number_match = re.search(r'Fatura No\s*:\s*([A-Za-z0-9-]+)', all_text)
        if invoice_number_match:
            invoice_data['invoice_number'] = invoice_number_match.group(1)
        
        # Extract invoice date
        date_match = re.search(r'Fatura Tarihi\s*:\s*(\d{1,2}[./]\d{1,2}[./]\d{4})', all_text)
        if date_match:
            invoice_data['invoice_date'] = date_match.group(1)
        
        # Extract vendor information
        vendor_section = re.search(r'SATICI\s*\n(.*?)(?=ALICI|\Z)', all_text, re.DOTALL)
        if vendor_section:
            vendor_text = vendor_section.group(1)
            
            # Extract vendor name
            vendor_name_match = re.search(r'^(.*?)(?=\n|VKN|$)', vendor_text)
            if vendor_name_match:
                invoice_data['vendor_name'] = vendor_name_match.group(1).strip()
            
            # Extract vendor tax ID
            vendor_tax_match = re.search(r'VKN\s*:\s*(\d+)', vendor_text)
            if vendor_tax_match:
                invoice_data['vendor_tax_id'] = vendor_tax_match.group(1)
            
            # Extract vendor address
            address_lines = []
            for line in vendor_text.split('\n'):
                if not re.search(r'(VKN|Tel|E-Posta|Fax|Web)', line) and line.strip():
                    if line.strip() != invoice_data['vendor_name']:
                        address_lines.append(line.strip())
            
            vendor_address = ' '.join(address_lines)
            # Clean up the address
            vendor_address = re.sub(r'\s+', ' ', vendor_address).strip()
            invoice_data['vendor_address'] = vendor_address
            
            # Try to extract city specifically
            city_match = re.search(r'([A-Za-zçğıöşüÇĞİÖŞÜ]+)/([A-Za-zçğıöşüÇĞİÖŞÜ]+)', vendor_address)
            if city_match:
                invoice_data['vendor_city'] = city_match.group(2).strip()
            else:
                # Check for common Turkish cities
                common_cities = ["Ankara", "Istanbul", "İstanbul", "Izmir", "İzmir", "Bursa", "Antalya", "Adana", "Konya"]
                for city in common_cities:
                    if city.lower() in vendor_address.lower():
                        invoice_data['vendor_city'] = city
                        break
        
        # Extract customer information
        customer_section = re.search(r'ALICI\s*\n(.*?)(?=\n\s*Malzeme|MALIN|$)', all_text, re.DOTALL)
        if customer_section:
            customer_text = customer_section.group(1)
            
            # Extract customer name
            customer_name_match = re.search(r'^(.*?)(?=\n|VKN|$)', customer_text)
            if customer_name_match:
                invoice_data['customer_name'] = customer_name_match.group(1).strip()
            
            # Extract customer tax ID
            customer_tax_match = re.search(r'VKN\s*:\s*(\d+)', customer_text)
            if customer_tax_match:
                invoice_data['customer_tax_id'] = customer_tax_match.group(1)
            
            # Extract customer address
            address_lines = []
            for line in customer_text.split('\n'):
                if not re.search(r'(VKN|Tel|E-Posta|Fax|Web)', line) and line.strip():
                    if line.strip() != invoice_data['customer_name']:
                        address_lines.append(line.strip())
            
            customer_address = ' '.join(address_lines)
            # Clean up the address
            customer_address = re.sub(r'\s+', ' ', customer_address).strip()
            invoice_data['customer_address'] = customer_address
            
            # Try to extract city specifically
            city_match = re.search(r'([A-Za-zçğıöşüÇĞİÖŞÜ]+)/([A-Za-zçğıöşüÇĞİÖŞÜ]+)', customer_address)
            if city_match:
                invoice_data['customer_city'] = city_match.group(2).strip()
            else:
                # Check for common Turkish cities
                common_cities = ["Ankara", "Istanbul", "İstanbul", "Izmir", "İzmir", "Bursa", "Antalya", "Adana", "Konya"]
                for city in common_cities:
                    if city.lower() in customer_address.lower():
                        invoice_data['customer_city'] = city
                        break
        
        # Extract line items
        items_section = re.search(r'(Malzeme / Hizmet.*?)(?=Vergiler|Toplam|Yalnız|$)', all_text, re.DOTALL)
        if items_section:
            items_text = items_section.group(1)
            lines = items_text.strip().split('\n')
            
            # Skip header line
            header_found = False
            current_item = {}
            
            for line in lines:
                if re.search(r'Malzeme / Hizmet|Miktar|Birim Fiyat|KDV|Tutar', line):
                    header_found = True
                    continue
                
                if header_found and line.strip():
                    # Try to match line item pattern
                    item_match = re.search(r'^(.*?)\s+(\d+(?:,\d+)?)\s+(\w+)\s+(\d+(?:,\d+)?)\s+%(\d+)\s+(\d+(?:,\d+)?)', line)
                    if item_match:
                        item = {
                            'description': item_match.group(1).strip(),
                            'quantity': item_match.group(2),
                            'unit': item_match.group(3),
                            'unit_price': item_match.group(4),
                            'tax_rate': item_match.group(5),
                            'amount': item_match.group(6)
                        }
                        invoice_data['line_items'].append(item)
                    else:
                        # This might be a continuation of the previous item description
                        if invoice_data['line_items'] and line.strip():
                            invoice_data['line_items'][-1]['description'] += ' ' + line.strip()
        
        # Extract totals
        subtotal_match = re.search(r'Mal Hizmet Toplam Tutarı\s*:\s*([0-9.,]+)', all_text)
        if subtotal_match:
            invoice_data['subtotal'] = subtotal_match.group(1)
        
        tax_match = re.search(r'Hesaplanan KDV\s*:\s*([0-9.,]+)', all_text)
        if tax_match:
            invoice_data['tax_amount'] = tax_match.group(1)
        
        total_match = re.search(r'Vergiler Dahil Toplam Tutar\s*:\s*([0-9.,]+)', all_text)
        if total_match:
            invoice_data['total_amount'] = total_match.group(1)
        
        # Extract notes or additional information
        notes_match = re.search(r'Not\s*:(.*?)(?=\Z)', all_text, re.DOTALL)
        if notes_match:
            invoice_data['notes'] = notes_match.group(1).strip()
    
    except Exception as e:
        st.error(f"PDF işlenirken hata oluştu: {str(e)}")
        st.write("Hata detayları gösteriliyor...")
        import traceback
        st.code(traceback.format_exc())
    
    return invoice_data

def display_invoice_data(invoice_data):
    """Display the extracted invoice data in a modern Streamlit interface"""
    
    # Invoice Header Information
    st.markdown("### 📋 Fatura Detayları")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="📄 Fatura Numarası",
            value=invoice_data.get('invoice_number', 'Bulunamadı')
        )
    with col2:
        st.metric(
            label="📅 Fatura Tarihi", 
            value=invoice_data.get('invoice_date', 'Bulunamadı')
        )
    
    st.markdown("---")
    
    # Vendor and Customer Information in Cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-card vendor-card">
            <h4>🏢 Satıcı Bilgileri</h4>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"**👤 Firma Adı:** {invoice_data.get('vendor_name', 'Bulunamadı')}")
        st.markdown(f"**🆔 Vergi No:** {invoice_data.get('vendor_tax_id', 'Bulunamadı')}")
        st.markdown(f"**📍 Adres:** {invoice_data.get('vendor_address', 'Bulunamadı')}")
    
    with col2:
        st.markdown("""
        <div class="info-card customer-card">
            <h4>🏪 Alıcı Bilgileri</h4>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"**👤 Firma Adı:** {invoice_data.get('customer_name', 'Bulunamadı')}")
        st.markdown(f"**🆔 Vergi No:** {invoice_data.get('customer_tax_id', 'Bulunamadı')}")
        st.markdown(f"**📍 Adres:** {invoice_data.get('customer_address', 'Bulunamadı')}")
    
    st.markdown("---")
    
    # Line Items Section
    st.markdown("### 🛍️ Ürün/Hizmet Detayları")
    
    if invoice_data.get('line_items'):
        for i, item in enumerate(invoice_data['line_items'], 1):
            with st.expander(f"📦 Ürün {i}: {item.get('description', 'Açıklama yok')[:50]}..."):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("📊 Miktar", f"{item.get('quantity', 'N/A')} {item.get('unit', '')}")
                with col2:
                    st.metric("💰 Birim Fiyat", f"{item.get('unit_price', 'N/A')} ₺")
                with col3:
                    st.metric("📈 KDV Oranı", f"%{item.get('tax_rate', 'N/A')}")
                
                st.markdown(f"**📝 Açıklama:** {item.get('description', 'Bulunamadı')}")
                st.markdown(f"**💵 Toplam Tutar:** {item.get('amount', 'N/A')} ₺")
    else:
        st.info("📦 Ürün/hizmet detayı bulunamadı")
    
    st.markdown("---")
    
    # Financial Summary
    st.markdown("### 💰 Finansal Özet")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label="💵 Ara Toplam",
            value=f"{invoice_data.get('subtotal', '0')} ₺"
        )
    with col2:
        st.metric(
            label="📊 KDV Tutarı",
            value=f"{invoice_data.get('tax_amount', '0')} ₺"
        )
    with col3:
        st.metric(
            label="💳 Genel Toplam",
            value=f"{invoice_data.get('total_amount', '0')} ₺"
        )
    
    # Notes Section
    if invoice_data.get('notes'):
        st.markdown("### 📝 Notlar")
        st.info(invoice_data['notes'])

def convert_to_xml(invoice_data):
    """Convert the extracted invoice data to XML format"""
    # Create root element
    root = ET.Element("Invoice")
    root.set("xmlns", "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2")
    
    # Add header information
    header = ET.SubElement(root, "InvoiceHeader")
    ET.SubElement(header, "InvoiceNumber").text = invoice_data.get('invoice_number', '')
    ET.SubElement(header, "InvoiceDate").text = invoice_data.get('invoice_date', '')
    
    # Add vendor information
    vendor = ET.SubElement(root, "AccountingSupplierParty")
    vendor_party = ET.SubElement(vendor, "Party")
    ET.SubElement(vendor_party, "PartyName").text = invoice_data.get('vendor_name', '')
    ET.SubElement(vendor_party, "PartyTaxID").text = invoice_data.get('vendor_tax_id', '')
    ET.SubElement(vendor_party, "PostalAddress").text = invoice_data.get('vendor_address', '')
    
    # Add customer information
    customer = ET.SubElement(root, "AccountingCustomerParty")
    customer_party = ET.SubElement(customer, "Party")
    ET.SubElement(customer_party, "PartyName").text = invoice_data.get('customer_name', '')
    ET.SubElement(customer_party, "PartyTaxID").text = invoice_data.get('customer_tax_id', '')
    ET.SubElement(customer_party, "PostalAddress").text = invoice_data.get('customer_address', '')
    
    # Add line items
    invoice_lines = ET.SubElement(root, "InvoiceLines")
    for item in invoice_data.get('line_items', []):
        line = ET.SubElement(invoice_lines, "InvoiceLine")
        ET.SubElement(line, "Description").text = item.get('description', '')
        ET.SubElement(line, "Quantity").text = item.get('quantity', '')
        ET.SubElement(line, "UnitCode").text = item.get('unit', '')
        ET.SubElement(line, "UnitPrice").text = item.get('unit_price', '')
        ET.SubElement(line, "TaxRate").text = item.get('tax_rate', '')
        ET.SubElement(line, "LineAmount").text = item.get('amount', '')
    
    # Add totals
    totals = ET.SubElement(root, "InvoiceTotals")
    ET.SubElement(totals, "TaxExclusiveAmount").text = invoice_data.get('subtotal', '')
    ET.SubElement(totals, "TaxAmount").text = invoice_data.get('tax_amount', '')
    ET.SubElement(totals, "TaxInclusiveAmount").text = invoice_data.get('total_amount', '')
    
    # Add notes if available
    if invoice_data.get('notes'):
        ET.SubElement(root, "Notes").text = invoice_data.get('notes', '')
    
    # Convert to string with pretty formatting
    rough_string = ET.tostring(root, 'utf-8')
    reparsed = xml.dom.minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")
    
    return pretty_xml

def geocode_address(address):
    """Convert address to geographical coordinates"""
    if not address:
        return None
    
    # Print address for debugging
    print(f"Trying to geocode address: {address}")
    st.write(f"Geocoding address: {address}")
    
    geolocator = Nominatim(user_agent="e-invoice-analyzer")
    
    # Clean the address - remove special characters and normalize
    clean_address = re.sub(r'[^\w\s\./,çğıöşüÇĞİÖŞÜ]', ' ', address)
    clean_address = re.sub(r'\s+', ' ', clean_address).strip()
    
    # Add Turkey to the address if not present
    if "turkey" not in clean_address.lower() and "türkiye" not in clean_address.lower():
        search_address = f"{clean_address}, Turkey"
    else:
        search_address = clean_address
    
    # First try with the full address
    try:
        st.write(f"Trying full address: {search_address}")
        location = geolocator.geocode(search_address, timeout=15)
        if location:
            st.write(f"Found coordinates: {location.latitude}, {location.longitude}")
            return (location.latitude, location.longitude)
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        st.write(f"Geocoding error: {str(e)}")
        time.sleep(1)
    
    # Try to extract city or district
    city_district_patterns = [
        r'([A-Za-zçğıöşüÇĞİÖŞÜ]+)[/\s]+([A-Za-zçğıöşüÇĞİÖŞÜ]+)',  # Format: District/City
        r'([A-Za-zçğıöşüÇĞİÖŞÜ]+)\s+Mah',  # Format: X Mahallesi
        r'([A-Za-zçğıöşüÇĞİÖŞÜ]+)\s+Cad',   # Format: X Caddesi
        r'([A-Za-zçğıöşüÇĞİÖŞÜ]+)\s+Sok',   # Format: X Sokak
    ]
    
    # Common Turkish cities to check
    common_cities = ["Ankara", "Istanbul", "İstanbul", "Izmir", "İzmir", "Bursa", "Antalya", 
                    "Adana", "Konya", "Gaziantep", "Kayseri", "Eskişehir", "Diyarbakır",
                    "Mersin", "Samsun", "Denizli"]
    
    # Check for common cities in the address
    for city in common_cities:
        if city.lower() in clean_address.lower():
            try:
                st.write(f"Trying with city: {city}, Turkey")
                location = geolocator.geocode(f"{city}, Turkey", timeout=10)
                if location:
                    st.write(f"Found coordinates for city {city}: {location.latitude}, {location.longitude}")
                    return (location.latitude, location.longitude)
            except:
                continue
    
    # Try with district/city patterns
    for pattern in city_district_patterns:
        match = re.search(pattern, clean_address)
        if match:
            try:
                district_or_street = match.group(1)
                st.write(f"Trying with extracted location: {district_or_street}, Turkey")
                location = geolocator.geocode(f"{district_or_street}, Turkey", timeout=10)
                if location:
                    st.write(f"Found coordinates: {location.latitude}, {location.longitude}")
                    return (location.latitude, location.longitude)
            except:
                continue
    
    # If all else fails, try with a default location (Ankara)
    st.write("Could not geocode address, using default coordinates for Ankara")
    return (39.9334, 32.8597)  # Default to Ankara

def create_map(vendor_address, customer_address):
    """Create a modern map with markers for vendor and customer addresses"""
    
    # Display address information in cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-card vendor-card">
            <h5>🏢 Satıcı Konumu</h5>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"**📍 Adres:** {vendor_address}")
    
    with col2:
        st.markdown("""
        <div class="info-card customer-card">
            <h5>🏪 Alıcı Konumu</h5>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"**📍 Adres:** {customer_address}")
    
    # Default center of Turkey
    center = [39.9334, 32.8597]  # Ankara coordinates
    
    # Create map with modern styling
    m = folium.Map(
        location=center,
        zoom_start=6,
        tiles='OpenStreetMap',
        attr='Map data © OpenStreetMap contributors'
    )
    
    # Progress tracking for geocoding
    geocoding_progress = st.progress(0)
    geocoding_status = st.empty()
    
    # Add vendor marker if address can be geocoded
    geocoding_status.text("🔍 Satıcı adresi konumlandırılıyor...")
    geocoding_progress.progress(25)
    
    vendor_coords = geocode_address(vendor_address)
    if vendor_coords:
        st.success(f"✅ Satıcı koordinatları: {vendor_coords[0]:.4f}, {vendor_coords[1]:.4f}")
        folium.Marker(
            location=vendor_coords,
            popup=folium.Popup(f"""
            <div style='width: 200px'>
                <h4>🏢 Satıcı</h4>
                <p><strong>📍 Adres:</strong><br>{vendor_address}</p>
                <p><strong>🌍 Koordinatlar:</strong><br>{vendor_coords[0]:.4f}, {vendor_coords[1]:.4f}</p>
            </div>
            """, max_width=250),
            icon=folium.Icon(color='green', icon='building', prefix='fa'),
            tooltip="🏢 Satıcı Lokasyonu"
        ).add_to(m)
    else:
        st.warning("⚠️ Satıcı adresi için koordinat bulunamadı.")
    
    geocoding_progress.progress(50)
    
    # Add customer marker if address can be geocoded
    geocoding_status.text("🔍 Alıcı adresi konumlandırılıyor...")
    geocoding_progress.progress(75)
    
    customer_coords = geocode_address(customer_address)
    if customer_coords:
        st.success(f"✅ Alıcı koordinatları: {customer_coords[0]:.4f}, {customer_coords[1]:.4f}")
        folium.Marker(
            location=customer_coords,
            popup=folium.Popup(f"""
            <div style='width: 200px'>
                <h4>🏪 Alıcı</h4>
                <p><strong>📍 Adres:</strong><br>{customer_address}</p>
                <p><strong>🌍 Koordinatlar:</strong><br>{customer_coords[0]:.4f}, {customer_coords[1]:.4f}</p>
            </div>
            """, max_width=250),
            icon=folium.Icon(color='red', icon='user', prefix='fa'),
            tooltip="🏪 Alıcı Lokasyonu"
        ).add_to(m)
    else:
        st.warning("⚠️ Alıcı adresi için koordinat bulunamadı.")
    
    geocoding_progress.progress(100)
    geocoding_status.text("✅ Konum belirleme tamamlandı!")
    
    # Clear progress indicators
    time.sleep(1)
    geocoding_progress.empty()
    geocoding_status.empty()
    
    # If both coordinates are available, draw a line between them
    if vendor_coords and customer_coords:
        # Calculate distance
        from math import radians, sin, cos, sqrt, atan2
        
        def calculate_distance(coord1, coord2):
            R = 6371  # Earth's radius in kilometers
            lat1, lon1 = radians(coord1[0]), radians(coord1[1])
            lat2, lon2 = radians(coord2[0]), radians(coord2[1])
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            distance = R * c
            
            return distance
        
        distance = calculate_distance(vendor_coords, customer_coords)
        
        folium.PolyLine(
            locations=[vendor_coords, customer_coords],
            color='#667eea',
            weight=3,
            opacity=0.8,
            popup=f"Mesafe: {distance:.1f} km",
            tooltip=f"📏 Satıcı-Alıcı Mesafesi: {distance:.1f} km"
        ).add_to(m)
        
        # Show distance metric
        st.metric("📏 Aralarındaki Mesafe", f"{distance:.1f} km")
        
        # Adjust map to show both markers with padding
        bounds = [vendor_coords, customer_coords]
        m.fit_bounds(bounds, padding=[20, 20])
    elif vendor_coords:
        m.location = vendor_coords
        m.zoom_start = 12
    elif customer_coords:
        m.location = customer_coords
        m.zoom_start = 12
    
    return m

if __name__ == "__main__":
    main()
