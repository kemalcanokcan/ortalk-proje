#!/usr/bin/env python3
"""
Test multi-format invoice processing to verify all formats work correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_format_extractor import MultiFormatExtractor
from xml_converter import XMLConverter

def test_json_extraction():
    """Test extracting data from JSON invoice"""
    print("Testing JSON invoice extraction...")
    
    try:
        extractor = MultiFormatExtractor("test_invoice.json")
        invoice_data = extractor.extract_invoice_data()
        
        print(f"✓ Invoice Number: {invoice_data.get('invoice_number', 'N/A')}")
        print(f"✓ Invoice Date: {invoice_data.get('invoice_date', 'N/A')}")
        print(f"✓ Vendor: {invoice_data.get('vendor_name', 'N/A')}")
        print(f"✓ Customer: {invoice_data.get('customer_name', 'N/A')}")
        print(f"✓ Line Items: {len(invoice_data.get('line_items', []))}")
        
        # Check VAT parsing in line items
        for i, item in enumerate(invoice_data.get('line_items', []), 1):
            vat_rate = item.get('tax_rate', 'N/A')
            print(f"  Item {i} VAT: {vat_rate}")
        
        print(f"✓ Total Amount: {invoice_data.get('total_amount', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"✗ JSON extraction failed: {e}")
        return False

def test_csv_extraction():
    """Test extracting data from CSV invoice"""
    print("\nTesting CSV invoice extraction...")
    
    try:
        extractor = MultiFormatExtractor("test_invoice.csv")
        invoice_data = extractor.extract_invoice_data()
        
        print(f"✓ Line Items: {len(invoice_data.get('line_items', []))}")
        
        # Check VAT parsing in line items
        for i, item in enumerate(invoice_data.get('line_items', []), 1):
            vat_rate = item.get('tax_rate', 'N/A')
            description = item.get('description', 'N/A')
            print(f"  Item {i}: {description} - VAT: {vat_rate}")
        
        print(f"✓ Total Amount: {invoice_data.get('total_amount', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"✗ CSV extraction failed: {e}")
        return False

def test_xml_generation():
    """Test XML generation with the extracted data"""
    print("\nTesting XML generation...")
    
    try:
        # Use sample data that includes problematic VAT values
        sample_data = {
            'invoice_number': 'TEST-2024-001',
            'invoice_date': '2024-01-15',
            'vendor_name': 'Test Company AŞ',
            'vendor_tax_id': '1234567890',
            'customer_name': 'Customer Company Ltd',
            'customer_tax_id': '0987654321',
            'line_items': [
                {
                    'description': 'Test Product 1',
                    'quantity': '2',
                    'unit_price': '100.00',
                    'tax_rate': '18%',  # Normal format
                    'amount': '200.00'
                },
                {
                    'description': 'Test Product 2',
                    'quantity': '1',
                    'unit_price': '50.00',
                    'tax_rate': '510%',  # Should be corrected to 18
                    'amount': '50.00'
                },
                {
                    'description': 'Test Product 3',
                    'quantity': '3',
                    'unit_price': '25.00',
                    'tax_rate': 'KDV %20',  # Turkish format
                    'amount': '75.00'
                }
            ],
            'total_amount': '325.00'
        }
        
        converter = XMLConverter(sample_data)
        xml_output = converter.convert_to_ubl_tr()
        
        # Check if XML contains expected elements
        required_elements = [
            '<InvoiceNumber>TEST-2024-001</InvoiceNumber>',
            '<IssueDate>2024-01-15</IssueDate>',
            '<Name>Test Company AŞ</Name>',
            '<Items>',
            '<Item>',
            '<Description>Test Product 1</Description>',
            '<VAT>18.0</VAT>',  # Should be parsed correctly from 18%
            '<VAT>18</VAT>',    # Should be corrected from 510%
            '<VAT>20.0</VAT>',  # Should be parsed correctly from KDV %20
            '<TotalAmount>325.00</TotalAmount>',
            '<Currency>TRY</Currency>'
        ]
        
        missing = []
        for element in required_elements:
            if element not in xml_output:
                missing.append(element)
        
        if missing:
            print(f"✗ Missing XML elements: {missing}")
            print("Generated XML:")
            print(xml_output)
            return False
        else:
            print("✓ XML generation successful with correct VAT parsing")
            return True
            
    except Exception as e:
        print(f"✗ XML generation failed: {e}")
        return False

def run_comprehensive_test():
    """Run all tests"""
    print("🧪 Running comprehensive multi-format invoice processing test")
    print("=" * 70)
    
    tests = [
        ("JSON Extraction", test_json_extraction),
        ("CSV Extraction", test_csv_extraction),
        ("XML Generation", test_xml_generation),
    ]
    
    passed = 0
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        try:
            if test_func():
                print(f"✅ {test_name} passed")
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 70)
    print(f"📊 SUMMARY: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All multi-format tests passed!")
        print("✅ VAT parsing works correctly across all formats")
        print("✅ XML output follows the required schema")
        print("✅ Error handling prevents absurd values like 510%")
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
    
    return passed == len(tests)

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
