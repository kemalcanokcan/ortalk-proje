#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to fix XML tags in the generated XML file
"""

def fix_xml_tags(input_file, output_file):
    """Fix XML tags in the input file and write to output file"""
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the Name tags
    content = content.replace("<n>", "<Name>").replace("</n>", "</Name>")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    """Run the script"""
    input_file = "test_invoice.xml"
    output_file = "fixed_invoice.xml"
    
    fix_xml_tags(input_file, output_file)
    print(f"Fixed XML written to {output_file}")
    
    # Read and print the fixed XML
    with open(output_file, 'r', encoding='utf-8') as f:
        xml_content = f.read()
    
    print("\n=== Fixed XML Content ===\n")
    print(xml_content)

if __name__ == "__main__":
    main()
