@echo off
echo E-Fatura PDF Analiz Sistemi baslatiliyor...
echo.
echo Tarayicinizda su adresi acin: http://localhost:8501
echo.
echo Uygulamayi durdurmak icin Ctrl+C basin.
echo.
python -m streamlit run main.py --server.port 8501
pause
