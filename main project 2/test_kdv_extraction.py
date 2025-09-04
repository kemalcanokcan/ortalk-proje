#!/usr/bin/env python3
"""
Test script for updated KDV, customer, and address extraction regex patterns
"""

import re

def test_kdv_patterns():
    """Test KDV extraction patterns"""
    print("=== Testing KDV Extraction Patterns ===\n")
    
    # Test texts from invoice photos
    test_texts = [
        "KDV (%20): 148.000,00 TL",
        "KDV Oranı: %20",
        "KDV Tutarı: 513,55 TL",
        "18% KDV",
        "Hesaplanan KDV (%20)(%20): 199.335,07 TL",
        "KDV (%0.00) Matrahı: 352,42 TL",
        "KDV (% 0.00) Tutarı: 0,00 TL",
        "KDV % 20",
        "513,55TL KDV",
        "KDV: 148.000,00",
        "KDV: %18",
        "%20 KDV: 148.000,00",
        "20% KDV",
        "KDV 18%"
    ]
    
    # KDV patterns to test
    kdv_patterns = [
        # Standard KDV patterns
        r'Hesaplanan\s+KDV\s*:?\s*([0-9.,]+)',
        r'HESAPLANAN\s+KDV\s*:?\s*([0-9.,]+)',
        r'KDV\s+Tutarı\s*:?\s*([0-9.,]+)',
        r'KDV\s+TUTARI\s*:?\s*([0-9.,]+)',
        r'Vergi\s+Tutarı\s*:?\s*([0-9.,]+)',
        r'Tax\s+Amount\s*:?\s*([0-9.,]+)',
        
        # KDV with percentage patterns
        r'KDV\s*\(%(\d+(?:[.,]\d+)?)\)\s*:?\s*([0-9.,]+)',
        r'KDV\s*\(%(\d+(?:[.,]\d+)?)\)\s*Matrahı\s*:?\s*([0-9.,]+)',
        r'KDV\s*\(%(\d+(?:[.,]\d+)?)\)\s*Tutarı\s*:?\s*([0-9.,]+)',
        r'Hesaplanan\s+KDV\s*\(%(\d+(?:[.,]\d+)?)\)\s*\(%(\d+(?:[.,]\d+)?)\)\s*:?\s*([0-9.,]+)',
        
        # KDV percentage patterns
        r'KDV\s*Oranı\s*:?\s*%(\d+(?:[.,]\d+)?)',
        r'KDV\s*ORANI\s*:?\s*%(\d+(?:[.,]\d+)?)',
        r'%(\d+(?:[.,]\d+)?)\s*KDV',
        r'KDV\s*%(\d+(?:[.,]\d+)?)',
        
        # KDV amount with currency
        r'KDV\s*Tutarı\s*:?\s*([0-9.,]+)\s*TL',
        r'KDV\s*TUTARI\s*:?\s*([0-9.,]+)\s*TL',
        r'([0-9.,]+)\s*TL\s*KDV',
        
        # Generic KDV patterns
        r'KDV\s*:?\s*([0-9.,]+)',
        r'KDV\s*:?\s*%(\d+(?:[.,]\d+)?)',
        r'%(\d+(?:[.,]\d+)?)\s*KDV\s*:?\s*([0-9.,]+)',
        
        # Fallback patterns
        r'(\d+(?:[.,]\d+)?)\s*%\s*(?:KDV|Vergi|Tax)',
        r'(?:KDV|Vergi|Tax)\s*(\d+(?:[.,]\d+)?)\s*%'
    ]
    
    for i, test_text in enumerate(test_texts, 1):
        print(f"Test {i}: {test_text}")
        matched = False
        
        for j, pattern in enumerate(kdv_patterns, 1):
            match = re.search(pattern, test_text, re.IGNORECASE)
            if match:
                groups = match.groups()
                print(f"  ✓ Pattern {j}: {pattern[:50]}...")
                print(f"    Groups: {groups}")
                matched = True
                break
        
        if not matched:
            print(f"  ✗ No pattern matched")
        print()

def test_customer_patterns():
    """Test customer extraction patterns"""
    print("=== Testing Customer Extraction Patterns ===\n")
    
    # Test texts from invoice photos
    test_texts = [
        "SAYIN KEMAL CAN OKCAN",
        "SAYIN Bahadır Yılmaz",
        "ALICI: ETİ MADEN İŞLETMELERİ",
        "MÜŞTERI: Point Internet Teknolojileri",
        "BUYER: EREN PERAKENDE VE TEKSTİL A.Ş.",
        "ETİ MADEN İŞLETMELERİ GENEL MÜDÜRLÜĞÜ",
        "GENEL MÜDÜRLÜĞÜ SATINALMA DAİRESİ BAŞKANLIĞI",
        "KEMAL CAN OKCAN",
        "Bahadır Yılmaz"
    ]
    
    # Customer patterns to test
    customer_patterns = [
        # Primary customer indicators (case-sensitive as requested)
        r'SAYIN\s*(.*?)(?=Malzeme|MALİN|ÜRÜN|HIZMET|e-FATURA|FATURA\s+NO|TOPLAM|$)',
        r'SAYIN\s*(.*?)(?=\n\s*[A-ZÜĞŞIÖÇ]{3,}|\n\s*\d|$)',
        
        # Standard patterns
        r'ALICI\s*:?\s*\n(.*?)(?=Malzeme|MALİN|ÜRÜN|HIZMET|e-FATURA|FATURA\s+NO|TOPLAM|$)',
        r'BUYER\s*:?\s*\n(.*?)(?=ITEM|PRODUCT|SERVICE|INVOICE|TOTAL|$)',
        r'MÜŞTERI\s*:?\s*\n(.*?)(?=ÜRÜN|HIZMET|TOPLAM|$)',
        r'ALICI\s*:?\s*(.*?)(?=Malzeme|MALİN|ÜRÜN|HIZMET|e-FATURA|FATURA\s+NO|TOPLAM|$)',
        r'BUYER\s*:?\s*(.*?)(?=ITEM|PRODUCT|SERVICE|INVOICE|TOTAL|$)',
        r'MÜŞTERI\s*:?\s*(.*?)(?=ÜRÜN|HIZMET|TOPLAM|$)',
        
        # Company-specific patterns
        r'(ETİ\s+MADEN.*?)(?=e-FATURA|Sıra\s+No|MALZEME|$)',
        r'(.*?GENEL\s+MÜDÜRLÜĞÜ.*?)(?=MALZEME|ÜRÜN|$)',
        r'(.*?(?:MÜDÜRLÜĞÜ|BAŞKANLIĞI|DAİRESİ).*?)(?=MALZEME|$)',
        
        # VKN-based patterns for customer
        r'(?:ALICI|BUYER).*?(.*?VKN\s*:?\s*\d{10}.*?)(?=MALZEME|ÜRÜN|$)',
        
        # Address-based customer identification
        r'(.*?KIZILIRMAK\s+MAH.*?ÇUKURAMBAR.*?ANKARA)(?=MALZEME|ÜRÜN|$)',
        r'(.*?ÇUKURAMBAR.*?ANKARA)(?=MALZEME|ÜRÜN|$)',
        r'(.*?06530.*?ANKARA)(?=MALZEME|ÜRÜN|$)',
        
        # Fallback patterns
        r'(?:ALICI|BUYER)(.*?)(?=\n\s*\d|\n\s*[A-Z]{3,})',
        r'(.*?)(?=Malzeme|MALZEME|ÜRÜN|HIZMET)',
        
        # Generic customer section after vendor
        r'(?:VKN|Vergi|Tel|E-Posta).*?\n(.*?)(?=Malzeme|MALİN|ÜRÜN|HIZMET|e-FATURA|$)'
    ]
    
    for i, test_text in enumerate(test_texts, 1):
        print(f"Test {i}: {test_text}")
        matched = False
        
        for j, pattern in enumerate(customer_patterns, 1):
            match = re.search(pattern, test_text, re.DOTALL | re.IGNORECASE)
            if match:
                groups = match.groups()
                print(f"  ✓ Pattern {j}: {pattern[:50]}...")
                print(f"    Groups: {groups}")
                matched = True
                break
        
        if not matched:
            print(f"  ✗ No pattern matched")
        print()

def test_address_patterns():
    """Test address extraction patterns"""
    print("=== Testing Address Extraction Patterns ===\n")
    
    # Test texts from invoice photos
    test_texts = [
        "06570 İnönü Bulvarı No:18, Yücetepe Turkiye, 06570/ ANKARA",
        "06530 KIZILIRMAK MAH. 1443 CAD.NO:5NO:1/A ÇANKAYA / ANKARA",
        "KONUTKENT MAH.3028.CADDE16A-173 ÇAYYOLU ÇANKAYA / ANKARA",
        "Atatürk Mah. Ertuğrul Gazi Sok. Metropol İstanbul Sit. C2 Apt. No: 2A/14 34758 Ataşehir, İstanbul",
        "Üçtutlar mah. Binevler 20. sk. no:20 MERKEZ / ÇORUM",
        "ALEMDAG/ANKARA"
    ]
    
    # Address patterns to test
    address_patterns = [
        # DMO patterns (vendor - top section)
        r'(06570\s+İnönü\s+Bulvarı.*?Yücetepe.*?ANKARA)',
        r'(İnönü\s+Bulvarı.*?No\s*:?\s*18.*?Yücetepe.*?ANKARA)',
        r'(Yücetepe.*?İnönü.*?Bulvarı.*?ANKARA)',
        r'(İnönü\s+Bulvarı\s+No\s*:?\s*18.*?Yücetepe.*?ANKARA)',
        
        # Eti Maden patterns (customer - middle section)
        r'(06530\s+KIZILIRMAK\s+MAH\..*?ÇUKURAMBAR.*?ANKARA)',
        r'(Kızılırmak\s+Mahallesi.*?1443.*?Cadde.*?Çukurambar.*?ANKARA)',
        r'(1443\.\s*Cadde.*?Kızılırmak.*?ANKARA)',
        r'(KIZILIRMAK\s+MAH\..*?1443\.\s*CADDE.*?ÇUKURAMBAR.*?ANKARA)',
        
        # GBA Bilişim patterns (vendor)
        r'(KONUTKENT\s+MAH\..*?ÇAYYOLU.*?ANKARA)',
        r'(KONUTKENT\s+MAH\..*?3028.*?CADDE.*?ÇAYYOLU.*?ANKARA)',
        
        # Generic Turkish address patterns with postal codes
        r'(\d{5}\s+[A-ZÜĞŞIÖÇa-züğşıöç]+\s+(?:MAH|Mah|Mahallesi).*?[A-ZÜĞŞIÖÇa-züğşıöç]+)',
        r'([A-ZÜĞŞIÖÇa-züğşıöç]+\s+(?:MAH|Mah|Mahallesi).*?\d+\.\s*(?:CADDE|Cadde|Cad).*?[A-ZÜĞŞIÖÇa-züğşıöç]+)',
        r'([A-ZÜĞŞIÖÇa-züğşıöç]+\s+(?:BULVARI|Bulvarı|Bulvar).*?No\s*:?\s*\d+.*?[A-ZÜĞŞIÖÇa-züğşıöç]+)',
        r'([A-ZÜĞŞIÖÇa-züğşıöç]+\s+(?:SOKAK|Sokak|Sok).*?[A-ZÜĞŞIÖÇa-züğşıöç]+)',
        
        # Address patterns from invoice photos
        r'(\d{5}\s+[A-ZÜĞŞIÖÇa-züğşıöç]+\s+(?:MAH|Mah|Mahallesi).*?[A-ZÜĞŞIÖÇa-züğşıöç]+)',
        r'([A-ZÜĞŞIÖÇa-züğşıöç]+\s+(?:MAH|Mah|Mahallesi).*?\d+\.\s*(?:CADDE|Cadde|Cad).*?No\s*:?\s*\d+.*?[A-ZÜĞŞIÖÇa-züğşıöç]+)',
        r'([A-ZÜĞŞIÖÇa-züğşıöç]+\s+(?:BULVARI|Bulvarı|Bulvar).*?No\s*:?\s*\d+.*?[A-ZÜĞŞIÖÇa-züğşıöç]+)',
        r'([A-ZÜĞŞIÖÇa-züğşıöç]+\s+(?:SOKAK|Sokak|Sok).*?No\s*:?\s*\d+.*?[A-ZÜĞŞIÖÇa-züğşıöç]+)',
        
        # City/district patterns
        r'([A-ZÜĞŞIÖÇa-züğşıöç]+\s*/\s*[A-ZÜĞŞIÖÇa-züğşıöç]+)',
        r'([A-ZÜĞŞIÖÇa-züğşıöç]+\s+[A-ZÜĞŞIÖÇa-züğşıöç]+)'
    ]
    
    for i, test_text in enumerate(test_texts, 1):
        print(f"Test {i}: {test_text}")
        matched = False
        
        for j, pattern in enumerate(address_patterns, 1):
            match = re.search(pattern, test_text, re.IGNORECASE | re.DOTALL)
            if match:
                groups = match.groups()
                print(f"  ✓ Pattern {j}: {pattern[:50]}...")
                print(f"    Groups: {groups}")
                matched = True
                break
        
        if not matched:
            print(f"  ✗ No pattern matched")
        print()

if __name__ == "__main__":
    test_kdv_patterns()
    test_customer_patterns()
    test_address_patterns()
    print("=== Testing Complete ===")
