#!/usr/bin/env python3
"""
Simple VAT parsing test to verify the fixes work correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_extractor import PDFExtractor

def test_vat_parsing():
    """Test VAT parsing with various input formats"""
    
    # Create a dummy extractor to test the VAT parsing method
    class DummyExtractor(PDFExtractor):
        def __init__(self):
            self.pdf_path = "dummy"
            self.text_content = ""
            self.tables = []
    
    extractor = DummyExtractor()
    
    # Test cases that should be parsed correctly
    test_cases = [
        # Format: (input, expected_output, description)
        ("18%", "18.0", "Simple percentage"),
        ("%18", "18.0", "Percentage at start"),
        ("KDV %18", "18.0", "Turkish VAT format"),
        ("VAT 18%", "18.0", "English VAT format"),
        ("Tax: 20%", "20.0", "Tax with colon"),
        ("8.5%", "8.5", "Decimal percentage"),
        
        # Test cases that should be corrected from absurd values
        ("510%", "18", "Absurd value should default"),
        ("1800", "18", "1800 should default (too high)"),
        ("180", "18", "180 should default (too high)"),
        ("200", "18", "200 should default (too high)"),
        
        # Edge cases
        ("", "18", "Empty string should default"),
        ("0%", "18", "Zero should default"),
        ("-5%", "18", "Negative should default"),
        ("50%", "18", "Too high should default"),
    ]
    
    passed = 0
    failed = 0
    
    print("Testing VAT parsing functionality...")
    print("=" * 60)
    
    for input_val, expected, description in test_cases:
        result = extractor._parse_vat_rate(input_val)
        
        if result == expected:
            print(f"✓ PASS: '{input_val}' -> '{result}' ({description})")
            passed += 1
        else:
            print(f"✗ FAIL: '{input_val}' -> '{result}' (expected '{expected}') ({description})")
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    
    return failed == 0

if __name__ == "__main__":
    success = test_vat_parsing()
    if success:
        print("🎉 VAT parsing tests passed!")
    else:
        print("❌ Some VAT parsing tests failed!")
    sys.exit(0 if success else 1)
