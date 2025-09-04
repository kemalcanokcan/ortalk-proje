#!/usr/bin/env python3
"""
Test suite for VAT parsing functionality to ensure correct handling of different formats
and prevention of absurd values like 510%.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_extractor import PDFExtractor
from xml_converter import XMLConverter

def test_vat_parsing():
    """Test VAT parsing with various input formats"""
    
    # Create a dummy extractor to test the VAT parsing method
    class VATTester:
        def __init__(self):
            pass
        
        def _parse_vat_rate(self, vat_str, default_rate='18'):
            # Copy the VAT parsing logic here for testing
            if not vat_str:
                return default_rate
            
            import re
            vat_str = str(vat_str).strip()
            
            # First, try to find a percentage pattern
            percentage_patterns = [
                r'(?:KDV|VAT|Tax)?\s*[:%=]?\s*(\d{1,2}(?:[.,]\d{1,2})?)\s*%',
                r'(?:KDV|VAT|Tax)?\s*%\s*(\d{1,2}(?:[.,]\d{1,2})?)',
                r'(\d{1,2}(?:[.,]\d{1,2})?)\s*%',
                r'%\s*(\d{1,2}(?:[.,]\d{1,2})?)',
                r'(?:KDV|VAT|Tax)?\s*(?:rate|oran|oranı)?\s*[:%=]?\s*(\d{1,2}(?:[.,]\d{1,2})?)',
                r'(?:KDV|VAT|Tax)?\s*(\d{1,2}(?:[.,]\d{1,2})?)'
            ]
            
            for pattern in percentage_patterns:
                match = re.search(pattern, vat_str, re.IGNORECASE)
                if match:
                    vat_value = match.group(1).replace(',', '.')
                    try:
                        vat_float = float(vat_value)
                        if 0 <= vat_float <= 30:
                            return str(vat_float)
                    except ValueError:
                        continue
            
            # Clean number approach
            cleaned_vat = re.sub(r'[^\d.]', '', vat_str.replace('%', ''))
            
            try:
                vat_float = float(cleaned_vat)
                
                if vat_float > 100:
                    if 1000 <= vat_float <= 3000:
                        corrected = vat_float / 100
                        return str(corrected)
                    elif 100 <= vat_float < 1000:
                        corrected = vat_float / 10
                        return str(corrected)
                    else:
                        return default_rate
                elif vat_float <= 0:
                    return default_rate
                else:
                    if vat_float > 30:
                        return default_rate
                    return str(vat_float)
            except ValueError:
                return default_rate
    
    # Test cases that should be parsed correctly
    test_cases = [
        # Format: (input, expected_output, description)
        ("18%", "18.0", "Simple percentage"),
        ("%18", "18.0", "Percentage at start"),
        ("KDV %18", "18.0", "Turkish VAT format"),
        ("VAT 18%", "18.0", "English VAT format"),
        ("Tax: 20%", "20.0", "Tax with colon"),
        ("KDV: 8%", "8.0", "Turkish VAT with colon"),
        ("Value Added Tax: 25%", "25.0", "Full VAT text"),
        ("18", "18.0", "Number only"),
        ("20", "20.0", "Number only"),
        ("8.5%", "8.5", "Decimal percentage"),
        ("KDV oranı: %8", "8.0", "Turkish rate format"),
        
        # Test cases that should be corrected from absurd values
        ("510%", "18", "Absurd value should default"),
        ("1800", "18.0", "1800 should become 18"),
        ("180", "18.0", "180 should become 18"),
        ("200", "20.0", "200 should become 20"),
        ("2000", "20.0", "2000 should become 20"),
        
        # Edge cases
        ("", "18", "Empty string should default"),
        ("invalid", "18", "Invalid text should default"),
        ("0%", "18", "Zero should default"),
        ("-5%", "18", "Negative should default"),
        ("50%", "18", "Too high should default"),
    ]
    
    tester = VATTester()
    passed = 0
    failed = 0
    
    print("Testing VAT parsing functionality...")
    print("=" * 60)
    
    for input_val, expected, description in test_cases:
        result = tester._parse_vat_rate(input_val)
        
        if result == expected:
            print(f"✓ PASS: '{input_val}' -> '{result}' ({description})")
            passed += 1
        else:
            print(f"✗ FAIL: '{input_val}' -> '{result}' (expected '{expected}') ({description})")
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All VAT parsing tests passed!")
        return True
    else:
        print("❌ Some VAT parsing tests failed!")
        return False

def test_xml_schema_compliance():
    """Test that XML output follows the required schema"""
    
    # Sample invoice data
    sample_data = {
        'invoice_number': 'INV-2024-001',
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
                'tax_rate': '18',
                'amount': '200.00'
            },
            {
                'description': 'Test Product 2',
                'quantity': '1',
                'unit_price': '50.00',
                'tax_rate': '20%',  # Test VAT parsing
                'amount': '50.00'
            }
        ],
        'total_amount': '250.00'
    }
    
    # Convert to XML
    converter = XMLConverter(sample_data)
    xml_output = converter.convert_to_ubl_tr()
    
    print("\nTesting XML schema compliance...")
    print("=" * 60)
    
    # Check required elements
    required_elements = [
        '<InvoiceNumber>',
        '<IssueDate>',
        '<Seller>',
        '<Name>',
        '<VKN>',
        '<Buyer>',
        '<Items>',
        '<Item>',
        '<Description>',
        '<Quantity>',
        '<UnitPrice>',
        '<VAT>',
        '<Total>',
        '</Item>',
        '</Items>',
        '<TotalAmount>',
        '<Currency>',
        '</Invoice>'
    ]
    
    missing_elements = []
    for element in required_elements:
        if element not in xml_output:
            missing_elements.append(element)
    
    if not missing_elements:
        print("✓ All required XML elements are present")
        
        # Check VAT parsing in XML
        if '<VAT>20.0</VAT>' in xml_output:
            print("✓ VAT parsing worked correctly in XML (20% -> 20.0)")
        else:
            print("✗ VAT parsing failed in XML")
            return False
            
        print("✓ XML schema compliance test passed!")
        return True
    else:
        print("✗ Missing XML elements:")
        for element in missing_elements:
            print(f"  - {element}")
        return False

def test_multi_format_vat_consistency():
    """Test that VAT parsing is consistent across different file formats"""
    
    # Test cases with problematic VAT values
    test_vat_values = [
        "18%",      # Should stay 18
        "510%",     # Should become 18 (default due to absurd value)
        "1800",     # Should become 18
        "180",      # Should become 18
        "KDV %20",  # Should become 20
        "%8",       # Should become 8
    ]
    
    expected_results = ["18.0", "18", "18.0", "18.0", "20.0", "8.0"]
    
    print("\nTesting VAT consistency across formats...")
    print("=" * 60)
    
    # Test with PDF extractor logic
    extractor = PDFExtractor("dummy_path")  # We won't actually read a file
    
    passed = 0
    failed = 0
    
    for i, vat_input in enumerate(test_vat_values):
        try:
            result = extractor._parse_vat_rate(vat_input)
            expected = expected_results[i]
            
            if result == expected:
                print(f"✓ PASS: VAT '{vat_input}' -> '{result}'")
                passed += 1
            else:
                print(f"✗ FAIL: VAT '{vat_input}' -> '{result}' (expected '{expected}')")
                failed += 1
        except Exception as e:
            print(f"✗ ERROR: VAT '{vat_input}' caused exception: {e}")
            failed += 1
    
    print("=" * 60)
    print(f"VAT consistency test: {passed} passed, {failed} failed")
    
    return failed == 0

def run_all_tests():
    """Run all test suites"""
    print("🧪 Running comprehensive test suite for invoice parsing improvements")
    print("=" * 80)
    
    tests = [
        ("VAT Parsing", test_vat_parsing),
        ("XML Schema Compliance", test_xml_schema_compliance),
        ("Multi-format VAT Consistency", test_multi_format_vat_consistency),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} tests...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test suite failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    passed_suites = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed_suites += 1
    
    print(f"\nOverall: {passed_suites}/{len(results)} test suites passed")
    
    if passed_suites == len(results):
        print("🎉 All tests passed! The invoice parsing improvements are working correctly.")
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
    
    return passed_suites == len(results)

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
