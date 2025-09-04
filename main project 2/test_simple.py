#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basit test scripti - E-fatura PDF Analiz Sistemi
"""

import sys
import os

def test_imports():
    """Gerekli kütüphanelerin import edilebilirliğini test et"""
    print("🔍 Kütüphane importları test ediliyor...")
    
    try:
        import streamlit
        print("✅ Streamlit başarıyla import edildi")
    except ImportError as e:
        print(f"❌ Streamlit import hatası: {e}")
        return False
    
    try:
        import pdfplumber
        print("✅ PDFPlumber başarıyla import edildi")
    except ImportError as e:
        print(f"❌ PDFPlumber import hatası: {e}")
        return False
    
    try:
        import folium
        print("✅ Folium başarıyla import edildi")
    except ImportError as e:
        print(f"❌ Folium import hatası: {e}")
        return False
    
    try:
        import geopy
        print("✅ Geopy başarıyla import edildi")
    except ImportError as e:
        print(f"❌ Geopy import hatası: {e}")
        return False
    
    try:
        from streamlit_folium import folium_static
        print("✅ Streamlit-Folium başarıyla import edildi")
    except ImportError as e:
        print(f"❌ Streamlit-Folium import hatası: {e}")
        return False
    
    return True

def test_modules():
    """Özel modüllerin import edilebilirliğini test et"""
    print("\n🔍 Özel modüller test ediliyor...")
    
    try:
        from pdf_extractor import PDFExtractor
        print("✅ PDFExtractor başarıyla import edildi")
    except ImportError as e:
        print(f"❌ PDFExtractor import hatası: {e}")
        return False
    
    try:
        from xml_converter import XMLConverter
        print("✅ XMLConverter başarıyla import edildi")
    except ImportError as e:
        print(f"❌ XMLConverter import hatası: {e}")
        return False
    
    try:
        from geo_mapper import GeoMapper
        print("✅ GeoMapper başarıyla import edildi")
    except ImportError as e:
        print(f"❌ GeoMapper import hatası: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Temel fonksiyonaliteyi test et"""
    print("\n🔍 Temel fonksiyonalite test ediliyor...")
    
    try:
        # GeoMapper test
        from geo_mapper import GeoMapper
        geo_mapper = GeoMapper()
        print("✅ GeoMapper instance oluşturuldu")
        
        # Basit geocoding test (default koordinat dönmeli)
        coords = geo_mapper.geocode_address("Ankara")
        if coords:
            print(f"✅ Geocoding test başarılı: {coords}")
        else:
            print("⚠️ Geocoding test - koordinat bulunamadı ama hata yok")
        
        # XMLConverter test
        from xml_converter import XMLConverter
        test_data = {
            'invoice_number': 'TEST001',
            'invoice_date': '01.01.2024',
            'vendor_name': 'Test Şirketi',
            'line_items': []
        }
        xml_converter = XMLConverter(test_data)
        xml_content = xml_converter.convert_to_ubl_tr()
        
        if xml_content and len(xml_content) > 100:
            print("✅ XML dönüştürme test başarılı")
        else:
            print("❌ XML dönüştürme test başarısız")
            return False
            
    except Exception as e:
        print(f"❌ Temel fonksiyonalite test hatası: {e}")
        return False
    
    return True

def main():
    """Ana test fonksiyonu"""
    print("🚀 E-Fatura PDF Analiz Sistemi - Sistem Testi")
    print("=" * 50)
    
    # Test 1: Kütüphane importları
    if not test_imports():
        print("\n❌ Kütüphane import testleri başarısız!")
        return False
    
    # Test 2: Özel modüller
    if not test_modules():
        print("\n❌ Özel modül testleri başarısız!")
        return False
    
    # Test 3: Temel fonksiyonalite
    if not test_basic_functionality():
        print("\n❌ Temel fonksiyonalite testleri başarısız!")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Tüm testler başarıyla tamamlandı!")
    print("\n📝 Uygulamayı çalıştırmak için:")
    print("   streamlit run main.py")
    print("\n🌐 Tarayıcınızda şu adresi açın:")
    print("   http://localhost:8501")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
