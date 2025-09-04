@echo off
echo PDF Test Aracı
echo ---------------
echo.

if "%~1"=="" (
  echo Kullanım: test_pdf.bat [PDF_DOSYA_YOLU]
  echo Örnek: test_pdf.bat C:\faturalar\ornek.pdf
  exit /b 1
)

echo PDF dosyası test ediliyor: %1
echo.

py -3.13 pdf_test.py "%~1"
pause
