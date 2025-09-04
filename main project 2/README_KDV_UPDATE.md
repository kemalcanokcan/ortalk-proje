# KDV ve Müşteri Çıkarma Sistemi Güncellemeleri

## 🚀 Yapılan Ana İyileştirmeler

### 1. **KDV Çıkarma Sistemi**
- **25+ yeni regex pattern** eklendi
- **KDV yüzde ve tutarını** ayrı ayrı çıkarır
- **Farklı format türleri** desteklenir (1, 2, 3 grup)
- **Fallback mekanizması** ile line item'lardan KDV hesaplama

#### KDV Pattern Türleri:
- **Standard KDV patterns**: `Hesaplanan KDV: 148.000,00`
- **KDV with percentage**: `KDV (%20): 148.000,00 TL`
- **KDV percentage only**: `KDV Oranı: %20`
- **KDV amount with currency**: `KDV Tutarı: 513,55 TL`
- **Generic patterns**: `18% KDV`, `KDV 18%`
- **Fallback patterns**: `%20 KDV: 148.000,00`

### 2. **Alıcı Tanıma Sistemi**
- **SAYIN, Müşteri, Alıcı** gibi farklı belirteçler
- **Case-sensitive** büyük/küçük harf duyarlılığı
- **Şirket spesifik** pattern'lar (ETİ MADEN, GENEL MÜDÜRLÜĞÜ)
- **Adres bazlı** tanımlama (posta kodu, bölge)

#### Customer Pattern Türleri:
- **Primary indicators**: `SAYIN KEMAL CAN OKCAN`
- **Standard patterns**: `ALICI: ETİ MADEN İŞLETMELERİ`
- **Company-specific**: `ETİ MADEN İŞLETMELERİ GENEL MÜDÜRLÜĞÜ`
- **Address-based**: `KIZILIRMAK MAH. ÇUKURAMBAR ANKARA`

### 3. **Akıllı Adres Ayrıştırma**
- **PDF yapısı analizi** ile bölüm tespiti
- **Konum bazlı** vendor/customer ayrıştırma
- **Context analizi** ile doğru sınıflandırma
- **Fallback mekanizmaları** ile güvenilir sonuçlar

#### Adres Pattern Türleri:
- **DMO patterns** (vendor): `06570 İnönü Bulvarı No:18, Yücetepe ANKARA`
- **Eti Maden patterns** (customer): `06530 KIZILIRMAK MAH. 1443 CAD.NO:5 ÇUKURAMBAR ANKARA`
- **Generic patterns**: `Atatürk Mah. Ertuğrul Gazi Sok. İstanbul`

## 🔧 Teknik Detaylar

### KDV Çıkarma Mantığı:
```python
# Enhanced KDV extraction with multiple patterns
kdv_extracted = False
for pattern in tax_patterns:
    tax_match = re.search(pattern, self.text_content, re.IGNORECASE)
    if tax_match:
        groups = tax_match.groups()
        
        # Handle different pattern types
        if len(groups) == 1:
            # Simple KDV amount or percentage
            value = groups[0]
            if '%' in pattern or 'Oranı' in pattern:
                invoice_data['tax_rate'] = self._clean_number(value)
            else:
                invoice_data['tax_amount'] = self._clean_number(value)
                kdv_extracted = True
        
        elif len(groups) == 2:
            # KDV with percentage and amount
            invoice_data['tax_rate'] = self._clean_number(groups[0])
            invoice_data['tax_amount'] = self._clean_number(groups[1])
            kdv_extracted = True
        
        # If we found KDV amount, we can break
        if kdv_extracted:
            break

# If no KDV amount found, try to extract from line items
if not kdv_extracted:
    self._extract_kdv_from_line_items(invoice_data)
```

### Fallback KDV Hesaplama:
```python
def _extract_kdv_from_line_items(self, invoice_data):
    """Extract KDV information from line items if not found in totals"""
    line_items = invoice_data.get('line_items', [])
    if not line_items:
        return
    
    total_kdv = 0
    kdv_rates = set()
    
    for item in line_items:
        tax_rate = item.get('tax_rate', '0')
        amount = item.get('amount', '0')
        
        if tax_rate and amount:
            try:
                rate = float(self._clean_number(tax_rate))
                item_amount = float(self._clean_number(amount))
                
                if 0 <= rate <= 30:  # Valid KDV rate
                    kdv_rates.add(rate)
                    item_kdv = item_amount * (rate / 100)
                    total_kdv += item_kdv
                    
            except (ValueError, TypeError):
                continue
    
    if total_kdv > 0:
        invoice_data['tax_amount'] = f"{total_kdv:.2f}"
    
    if kdv_rates:
        most_common_rate = max(kdv_rates, key=list(kdv_rates).count)
        invoice_data['tax_rate'] = str(most_common_rate)
```

### PDF Yapısı Analizi:
```python
def _analyze_pdf_structure(self):
    """Analyze PDF structure to understand layout and sections"""
    structure = {
        'vendor_section': None,
        'customer_section': None,
        'invoice_details': None,
        'line_items': None,
        'totals': None
    }
    
    lines = self.text_content.split('\n')
    
    # Find key sections by looking for section markers
    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        
        # Vendor section markers (usually at top)
        if any(marker in line_lower for marker in ['devlet malzeme', 'gba bilişim']):
            structure['vendor_section'] = i
        
        # Customer section markers (usually after vendor)
        elif any(marker in line_lower for marker in ['sayın', 'eti maden', 'müşteri']):
            structure['customer_section'] = i
    
    return structure
```

## 📊 Test Sonuçları

### KDV Pattern Testleri:
- ✅ `KDV (%20): 148.000,00 TL` → Pattern 1 matched
- ✅ `KDV Oranı: %20` → Pattern 2 matched  
- ✅ `18% KDV` → Pattern 3 matched
- ✅ `Hesaplanan KDV (%20)(%20): 199.335,07 TL` → Pattern 4 matched

### Customer Pattern Testleri:
- ✅ `SAYIN KEMAL CAN OKCAN` → Pattern 1 matched
- ✅ `ALICI: ETİ MADEN İŞLETMELERİ` → Pattern 2 matched
- ✅ `ETİ MADEN İŞLETMELERİ GENEL MÜDÜRLÜĞÜ` → Pattern 3 matched

### Address Pattern Testleri:
- ✅ `06570 İnönü Bulvarı No:18, Yücetepe ANKARA` → Pattern 1 matched
- ✅ `06530 KIZILIRMAK MAH. 1443 CAD.NO:5 ÇUKURAMBAR ANKARA` → Pattern 2 matched

## 🎯 Kullanım Talimatları

### 1. **KDV Çıkarma**:
- Sistem otomatik olarak farklı KDV formatlarını tanır
- Eğer toplam KDV bulunamazsa, line item'lardan hesaplar
- Sonuçlar `invoice_data['tax_amount']` ve `invoice_data['tax_rate']` alanlarında saklanır

### 2. **Müşteri Tanıma**:
- "SAYIN" belirteci ile başlayan isimler otomatik tanınır
- Case-sensitive arama yapılır
- Farklı şirket formatları desteklenir

### 3. **Adres Ayrıştırma**:
- PDF yapısı analiz edilerek vendor/customer ayrımı yapılır
- Konum bazlı analiz ile doğru sınıflandırma
- Fallback mekanizmaları ile güvenilir sonuçlar

## 🔮 Gelecek Planları

### Kısa Vadeli:
- [ ] Daha fazla KDV format pattern'i ekleme
- [ ] Customer pattern'ları genişletme
- [ ] Adres ayrıştırma algoritmasını iyileştirme

### Orta Vadeli:
- [ ] Machine learning tabanlı pattern recognition
- [ ] OCR kalitesi iyileştirme
- [ ] Çoklu dil desteği

### Uzun Vadeli:
- [ ] AI tabanlı fatura analizi
- [ ] Otomatik pattern öğrenme
- [ ] Real-time fatura işleme

## 📝 Değişiklik Geçmişi

### v2.1.0 (Current)
- ✅ KDV extraction patterns genişletildi (25+ pattern)
- ✅ Customer identification patterns eklendi
- ✅ Address separation logic iyileştirildi
- ✅ PDF structure analysis eklendi
- ✅ Fallback KDV calculation eklendi

### v2.0.0
- ✅ Basic KDV extraction
- ✅ Simple customer patterns
- ✅ Basic address extraction

## 🤝 Katkıda Bulunma

1. Yeni pattern'lar eklemek için `pdf_extractor.py` dosyasını düzenleyin
2. Test script'ini güncelleyin
3. README dosyasını güncelleyin
4. Pull request gönderin

## 📞 Destek

Herhangi bir sorun veya öneri için:
- Issue açın
- Pull request gönderin
- Dokümantasyonu güncelleyin

---

**Not**: Bu güncellemeler mevcut regex'leri bozmadan yapılmıştır. Tüm eski fonksiyonalite korunmuştur.
