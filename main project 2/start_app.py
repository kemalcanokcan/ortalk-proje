#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E-Fatura PDF Analiz Sistemi - Başlatma Scripti
"""

import subprocess
import sys
import webbrowser
import time
import os

def main():
    print("🚀 E-Fatura PDF Analiz Sistemi")
    print("=" * 40)
    print("Uygulama başlatılıyor...")
    print()
    print("🌐 Tarayıcınızda otomatik olarak açılacak:")
    print("   http://localhost:8501")
    print()
    print("⚠️  Uygulamayı durdurmak için Ctrl+C basın")
    print("=" * 40)
    print()
    
    try:
        # Mevcut script'in bulunduğu dizine geç
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        print(f"📁 Çalışma dizini: {os.getcwd()}")
        print(f"🔍 main.py dosyası mevcut mu: {os.path.exists('main.py')}")
        print()
        
        # 2 saniye sonra tarayıcıyı aç
        def open_browser():
            time.sleep(2)
            webbrowser.open('http://localhost:8501')
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Streamlit'i başlat
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'main.py',
            '--server.port', '8501',
            '--server.headless', 'false'
        ])
        
    except KeyboardInterrupt:
        print("\n\n✅ Uygulama kapatıldı.")
    except Exception as e:
        print(f"\n❌ Hata oluştu: {e}")
        print("\nManuel başlatma için şu komutu kullanın:")
        print("python -m streamlit run main.py")

if __name__ == "__main__":
    main()
