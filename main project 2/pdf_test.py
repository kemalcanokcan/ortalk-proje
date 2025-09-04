import pdfplumber
import sys
import os

def test_pdf_extraction(pdf_path):
    """Test PDF extraction and print results"""
    print(f"Testing PDF extraction for: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}")
        return
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"PDF opened successfully. Number of pages: {len(pdf.pages)}")
            
            # Extract text from first page
            if len(pdf.pages) > 0:
                print("\nExtracting text from first page:")
                text = pdf.pages[0].extract_text()
                print(text[:500] + "..." if len(text) > 500 else text)
            
            # Extract tables from first page
            if len(pdf.pages) > 0:
                print("\nExtracting tables from first page:")
                tables = pdf.pages[0].extract_tables()
                if tables:
                    for i, table in enumerate(tables):
                        print(f"\nTable {i+1}:")
                        for row in table:
                            print(row)
                else:
                    print("No tables found on first page")
    
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_pdf_extraction(sys.argv[1])
    else:
        print("Usage: python pdf_test.py <path_to_pdf_file>")
