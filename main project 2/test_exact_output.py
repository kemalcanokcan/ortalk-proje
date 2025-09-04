#!/usr/bin/env python3
"""
Test to verify that the parser outputs exactly what's written on the invoice
without any normalization, correction, or inference.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from xml_converter import XMLConverter

def test_exact_vat_preservation():
    """Test that VAT rates are preserved exactly as written"""
    print("Testing exact VAT preservation...")
    
    test_cases = [
        {
            'input': '18%',
            'description': 'Simple percentage should stay as 18%'
        },
        {
            'input': 'KDV %20',
            'description': 'Turkish format should stay as KDV %20'
        },
        {
            'input': '%8',
            'description': 'Percent at start should stay as %8'
        },
        {
            'input': 'VAT 25%',
            'description': 'English format should stay as VAT 25%'
        },
        {
            'input': '510%',
            'description': 'Even absurd values should stay as 510%'
        }
    ]
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        sample_data = {
            'invoice_number': 'TEST-001',
            'invoice_date': '01/09/2025',  # Should stay as is
            'vendor_name': 'Test Company AŞ',
            'vendor_tax_id': '1234567890',
            'customer_name': 'Customer Company Ltd',
            'customer_tax_id': '0987654321',
            'line_items': [
                {
                    'description': 'Test Product',
                    'quantity': '2',
                    'unit_price': '100,50 ₺',  # Should preserve currency and comma
                    'tax_rate': test['input'],  # This is what we're testing
                    'amount': '201,00 ₺'
                }
            ],
            'total_amount': '237,18 ₺'  # Should preserve currency and comma
        }
        
        converter = XMLConverter(sample_data)
        xml_output = converter.convert_to_ubl_tr()
        
        # Check if the VAT rate appears exactly as input
        expected_vat_xml = f'<VAT>{test["input"]}</VAT>'
        
        if expected_vat_xml in xml_output:
            print(f"✓ PASS: {test['description']} - '{test['input']}' preserved exactly")
            passed += 1
        else:
            print(f"✗ FAIL: {test['description']} - '{test['input']}' was modified")
            print(f"  Expected: {expected_vat_xml}")
            print(f"  XML excerpt: {xml_output[xml_output.find('<VAT>'):xml_output.find('</VAT>')+6]}")
            failed += 1
    
    return passed, failed

def test_exact_formatting_preservation():
    """Test that all formatting is preserved exactly"""
    print("\nTesting exact formatting preservation...")
    
    sample_data = {
        'invoice_number': 'INV/2025/001',  # Should keep slashes
        'invoice_date': '01/09/2025',  # Should NOT convert to ISO
        'vendor_name': 'ACME CORPORATION LTD.',
        'vendor_tax_id': '12.345.678.901',  # Should keep dots
        'customer_name': 'Customer & Co.',  # Should keep ampersand
        'customer_tax_id': '98-765-432-10',  # Should keep dashes
        'line_items': [
            {
                'description': 'Product #1',
                'quantity': '2,5',  # Should keep comma decimal
                'unit_price': '1.234,56 €',  # Should keep European format
                'tax_rate': 'MwSt. 19%',  # Should keep German format
                'amount': '3.086,40 €'
            }
        ],
        'total_amount': '3.673,02 €',  # Should keep European format
        'currency': '€'  # Should keep euro symbol
    }
    
    converter = XMLConverter(sample_data)
    xml_output = converter.convert_to_ubl_tr()
    
    expected_values = [
        ('<InvoiceNumber>INV/2025/001</InvoiceNumber>', 'Invoice number with slashes'),
        ('<IssueDate>01/09/2025</IssueDate>', 'Date in original format'),
        ('<VKN>12.345.678.901</VKN>', 'Tax ID with dots'),
        ('<VKN>98-765-432-10</VKN>', 'Customer tax ID with dashes'),
        ('<Quantity>2,5</Quantity>', 'Quantity with comma decimal'),
        ('<UnitPrice>1.234,56 €</UnitPrice>', 'Unit price in European format'),
        ('<VAT>MwSt. 19%</VAT>', 'German VAT format'),
        ('<Total>3.086,40 €</Total>', 'Total with European formatting'),
        ('<TotalAmount>3.673,02 €</TotalAmount>', 'Grand total with Euro'),
        ('<Currency>€</Currency>', 'Euro currency symbol')
    ]
    
    passed = 0
    failed = 0
    
    for expected_xml, description in expected_values:
        if expected_xml in xml_output:
            print(f"✓ PASS: {description}")
            passed += 1
        else:
            print(f"✗ FAIL: {description}")
            print(f"  Expected: {expected_xml}")
            failed += 1
    
    return passed, failed

def test_empty_fields():
    """Test that empty fields remain empty instead of being filled with defaults"""
    print("\nTesting empty field handling...")
    
    sample_data = {
        'invoice_number': 'TEST-002',
        'invoice_date': '',  # Empty - should stay empty
        'vendor_name': 'Test Company',
        'vendor_tax_id': '',  # Empty - should stay empty
        'customer_name': 'Customer',
        'customer_tax_id': '',  # Empty - should stay empty
        'line_items': [
            {
                'description': 'Test Product',
                'quantity': '1',
                'unit_price': '',  # Empty - should stay empty
                'tax_rate': '',  # Empty - should stay empty (no default 18%)
                'amount': ''  # Empty - should stay empty
            }
        ],
        'total_amount': '',  # Empty - should stay empty
        'currency': ''  # Empty - should stay empty
    }
    
    converter = XMLConverter(sample_data)
    xml_output = converter.convert_to_ubl_tr()
    
    expected_empty_fields = [
        ('<IssueDate></IssueDate>', 'Empty date'),
        ('<VKN></VKN>', 'Empty vendor tax ID'),
        ('<UnitPrice></UnitPrice>', 'Empty unit price'),
        ('<VAT></VAT>', 'Empty VAT rate'),
        ('<Total></Total>', 'Empty line total'),
        ('<TotalAmount></TotalAmount>', 'Empty grand total'),
        ('<Currency></Currency>', 'Empty currency')
    ]
    
    passed = 0
    failed = 0
    
    for expected_xml, description in expected_empty_fields:
        if expected_xml in xml_output:
            print(f"✓ PASS: {description} - field left empty")
            passed += 1
        else:
            print(f"✗ FAIL: {description} - field was filled with default")
            failed += 1
    
    return passed, failed

def run_exact_output_tests():
    """Run all exact output tests"""
    print("🎯 Testing Exact Output Preservation")
    print("=" * 60)
    print("Verifying that the parser outputs exactly what's written")
    print("on the invoice without normalization or auto-correction.")
    print("=" * 60)
    
    total_passed = 0
    total_failed = 0
    
    # Test 1: VAT preservation
    passed, failed = test_exact_vat_preservation()
    total_passed += passed
    total_failed += failed
    
    # Test 2: Formatting preservation
    passed, failed = test_exact_formatting_preservation()
    total_passed += passed
    total_failed += failed
    
    # Test 3: Empty field handling
    passed, failed = test_empty_fields()
    total_passed += passed
    total_failed += failed
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 EXACT OUTPUT TEST SUMMARY")
    print("=" * 60)
    print(f"Total tests: {total_passed + total_failed}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    
    if total_failed == 0:
        print("🎉 SUCCESS: All values preserved exactly as written!")
        print("✅ No normalization or auto-correction applied")
        print("✅ Original formatting maintained")
        print("✅ Empty fields left empty")
    else:
        print("⚠️  Some values were modified from their original form")
        print("❌ Normalization or auto-correction may still be active")
    
    return total_failed == 0

if __name__ == "__main__":
    success = run_exact_output_tests()
    sys.exit(0 if success else 1)
