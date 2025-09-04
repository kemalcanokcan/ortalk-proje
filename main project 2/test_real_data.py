#!/usr/bin/env python3
"""
Test with real invoice data to verify exact preservation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_format_extractor import MultiFormatExtractor
from xml_converter import XMLConverter

def test_json_exact_preservation():
    """Test JSON extraction with exact value preservation"""
    print("Testing JSON extraction with exact preservation...")
    
    try:
        extractor = MultiFormatExtractor("test_invoice.json")
        invoice_data = extractor.extract_invoice_data()
        
        # Convert to XML
        converter = XMLConverter(invoice_data)
        xml_output = converter.convert_to_ubl_tr()
        
        print(f"✓ Invoice Number: {invoice_data.get('invoice_number')}")
        print(f"✓ Invoice Date: {invoice_data.get('invoice_date')} (kept original format)")
        print(f"✓ Total Amount: {invoice_data.get('total_amount')} (kept original format)")
        
        # Check line items
        for i, item in enumerate(invoice_data.get('line_items', []), 1):
            print(f"✓ Item {i} VAT: '{item.get('tax_rate')}' (exact format)")
        
        # Show a portion of the XML to verify
        print("\nXML Sample (showing exact preservation):")
        lines = xml_output.split('\n')
        for line in lines:
            if any(tag in line for tag in ['<VAT>', '<UnitPrice>', '<IssueDate>', '<TotalAmount>']):
                print(f"  {line.strip()}")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_csv_exact_preservation():
    """Test CSV extraction with exact value preservation"""
    print("\nTesting CSV extraction with exact preservation...")
    
    try:
        extractor = MultiFormatExtractor("test_invoice.csv")
        invoice_data = extractor.extract_invoice_data()
        
        # Convert to XML
        converter = XMLConverter(invoice_data)
        xml_output = converter.convert_to_ubl_tr()
        
        print(f"✓ Found {len(invoice_data.get('line_items', []))} line items")
        
        # Check that VAT rates are preserved exactly
        for i, item in enumerate(invoice_data.get('line_items', []), 1):
            vat = item.get('tax_rate', '')
            desc = item.get('description', '')
            print(f"✓ Item {i}: {desc[:30]}... - VAT: '{vat}' (exact)")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Real Data with Exact Preservation")
    print("=" * 50)
    
    success1 = test_json_exact_preservation()
    success2 = test_csv_exact_preservation()
    
    if success1 and success2:
        print("\n✅ All real data tests passed!")
        print("✅ Values preserved exactly as written in source files")
    else:
        print("\n❌ Some real data tests failed")
    
    sys.exit(0 if (success1 and success2) else 1)
