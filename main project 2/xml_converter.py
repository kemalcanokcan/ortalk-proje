import xml.etree.ElementTree as ET
import xml.dom.minidom
from datetime import datetime
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class XMLConverter:
    def __init__(self, invoice_data):
        """Initialize the XML converter with invoice data"""
        self.invoice_data = invoice_data
        
    def convert_to_ubl_tr(self):
        """Convert invoice data to E-Fatura format XML"""
        try:
            # Create XML string directly
            xml_parts = []
            xml_parts.append('<?xml version="1.0" encoding="UTF-8"?>')
            
            # Root element with attributes
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            xml_parts.append(f'<E-Fatura_Verileri Oluşturulma_Tarihi="{current_time}" Toplam_Fatura_Sayısı="1">')
            
            # Single invoice entry
            xml_parts.append('  <Fatura Sıra_No="1">')
            
            # Add invoice number
            invoice_number = self.invoice_data.get('invoice_number', '')
            if not invoice_number:
                logger.warning("Missing invoice number, using placeholder")
                invoice_number = f"INV-{self._generate_uuid()}"
            xml_parts.append(f'    <Fatura_No>{self._escape_xml(invoice_number)}</Fatura_No>')
            
            # Add issue date in DD-MM-YYYY format
            issue_date = self.invoice_data.get('invoice_date', '')
            formatted_date = self._format_date_turkish(issue_date)
            xml_parts.append(f'    <Fatura_Tarihi>{formatted_date}</Fatura_Tarihi>')
            
            # Add invoice type
            xml_parts.append('    <Fatura_Tipi>SATIS</Fatura_Tipi>')
            
            # Add ETTN (Electronic Invoice Number)
            ettn = self._generate_uuid()
            xml_parts.append(f'    <ETTN>{ettn}</ETTN>')
            
            # Add sender (vendor) information
            seller_name = self.invoice_data.get('vendor_name', '')
            if not seller_name:
                logger.warning("Missing seller name, using placeholder")
                seller_name = "Unknown Seller"
            xml_parts.append(f'    <Gönderen>{self._escape_xml(seller_name)}</Gönderen>')
            
            # Add sender address
            seller_address = self.invoice_data.get('vendor_address', '')
            if seller_address:
                xml_parts.append(f'    <Gönderen_Adres>{self._escape_xml(seller_address)}</Gönderen_Adres>')
            
            # Add sender tax office
            xml_parts.append('    <Gönderen_Vergi_Dairesi>ANKARA KURUMLAR</Gönderen_Vergi_Dairesi>')
            
            # Add sender VKN (tax ID)
            seller_vkn = self.invoice_data.get('vendor_tax_id', '')
            if not seller_vkn:
                logger.warning("Missing seller VKN (tax ID)")
                seller_vkn = "0000000000"
            xml_parts.append(f'    <Gönderen_VKN>vergi kimlik no: {seller_vkn}</Gönderen_VKN>')
            
            # Add sender website
            xml_parts.append('    <Gönderen_Web_Sitesi>www.dmo.gov.tr</Gönderen_Web_Sitesi>')
            
            # Add receiver (customer) information
            customer_name = self.invoice_data.get('customer_name', '')
            if not customer_name:
                logger.warning("Missing customer name, using placeholder")
                customer_name = "Unknown Customer"
            xml_parts.append(f'    <Alıcı>{self._escape_xml(customer_name)}</Alıcı>')
            
            # Add receiver address
            customer_address = self.invoice_data.get('customer_address', '')
            if customer_address:
                xml_parts.append(f'    <Alıcı_Adres>{self._escape_xml(customer_address)}</Alıcı_Adres>')
            
            # Add line items - process all items
            line_items = self.invoice_data.get('line_items', [])
            if line_items:
                # Calculate totals for all items
                total_invoice_amount = 0
                total_vat_amount = 0
                total_net_amount = 0
                all_descriptions = []
                
                # Process each line item
                for i, item in enumerate(line_items, 1):
                    logger.debug(f"Processing line item {i}: {item}")
                    
                    # Validate item data before XML creation
                    validated_item = self._validate_line_item(item, i)
                    
                    # Calculate amounts for this item
                    amount_str = validated_item.get('amount', '0')
                    if not amount_str or amount_str.strip() == '':
                        amount_str = '0'
                    item_total = float(amount_str)
                    
                    vat_rate_str = validated_item.get('tax_rate', '20')
                    if not vat_rate_str or vat_rate_str.strip() == '':
                        vat_rate_str = '20'
                    item_vat_rate = float(vat_rate_str)
                    
                    # Calculate VAT amount for this item
                    item_vat_amount = item_total * (item_vat_rate / 100)
                    item_net_amount = item_total - item_vat_amount
                    
                    # Add to totals
                    total_invoice_amount += item_total
                    total_vat_amount += item_vat_amount
                    total_net_amount += item_net_amount
                    
                    # Collect description for combined field
                    item_description = validated_item.get('description', f'Ürün {i}')
                    all_descriptions.append(item_description)
                    
                    logger.info(f"Item {i}: {item_description} - Amount: {item_total}, VAT: {item_vat_amount}")
                
                # Format total amounts in Turkish format
                total_formatted = self._format_amount_turkish(str(total_invoice_amount))
                vat_formatted = self._format_amount_turkish(str(total_vat_amount))
                net_formatted = self._format_amount_turkish(str(total_net_amount))
                
                # Add combined item information
                combined_description = '; '.join(all_descriptions)
                xml_parts.append(f'    <Mal_Hizmet_Adı>{self._escape_xml(combined_description)}</Mal_Hizmet_Adı>')
                
                # Use the most common VAT rate or first item's rate
                if line_items:
                    first_item = self._validate_line_item(line_items[0], 1)
                    vat_rate = first_item.get('tax_rate', '20')
                    if not vat_rate or vat_rate.strip() == '':
                        vat_rate = '20'
                else:
                    vat_rate = '20'
                xml_parts.append(f'    <KDV_Oranı>{vat_rate}</KDV_Oranı>')
                
                # Add total amounts
                xml_parts.append(f'    <KDV_Tutarı>{vat_formatted} TL</KDV_Tutarı>')
                xml_parts.append(f'    <Mal_Hizmet_Toplam_Tutarı>{net_formatted} TL</Mal_Hizmet_Toplam_Tutarı>')
                xml_parts.append(f'    <Vergiler_Dahil_Toplam_Tutar>{total_formatted} TL</Vergiler_Dahil_Toplam_Tutar>')
                xml_parts.append(f'    <Ödenecek_Tutar>{total_formatted} TL</Ödenecek_Tutar>')
                xml_parts.append(f'    <Satır_Toplam_Tutarı>{total_formatted} TL</Satır_Toplam_Tutarı>')
                xml_parts.append(f'    <Tüm_Mal_Hizmetler>{self._escape_xml(combined_description)}</Tüm_Mal_Hizmetler>')
                
                # Add individual line items as separate elements
                xml_parts.append('    <Fatura_Kalemleri>')
                for i, item in enumerate(line_items, 1):
                    validated_item = self._validate_line_item(item, i)
                    
                    xml_parts.append(f'      <Kalem_{i}>')
                    xml_parts.append(f'        <Açıklama>{self._escape_xml(validated_item.get("description", f"Ürün {i}"))}</Açıklama>')
                    xml_parts.append(f'        <Miktar>{validated_item.get("quantity", "1")}</Miktar>')
                    xml_parts.append(f'        <Birim>{validated_item.get("unit", "Adet")}</Birim>')
                    xml_parts.append(f'        <Birim_Fiyat>{self._format_amount_turkish(validated_item.get("unit_price", "0"))} TL</Birim_Fiyat>')
                    xml_parts.append(f'        <KDV_Oranı>{validated_item.get("tax_rate", "20")}</KDV_Oranı>')
                    xml_parts.append(f'        <Tutar>{self._format_amount_turkish(validated_item.get("amount", "0"))} TL</Tutar>')
                    xml_parts.append(f'      </Kalem_{i}>')
                xml_parts.append('    </Fatura_Kalemleri>')
                
                # Add standard fields
                xml_parts.append('    <İskonto_Oranı>0</İskonto_Oranı>')
                xml_parts.append('    <İskonto_Tutarı>0,00 TL</İskonto_Tutarı>')
                xml_parts.append(f'    <Hesaplanan_KDV>{vat_formatted} TL</Hesaplanan_KDV>')
                xml_parts.append('    <Diğer_Vergiler>0,00 TL</Diğer_Vergiler>')
                
                # Add quantity and unit info (from first item or combined)
                if line_items:
                    first_item = self._validate_line_item(line_items[0], 1)
                    total_quantity = sum(self._extract_numeric_value(self._validate_line_item(item, i+1).get('quantity', '1')) for i, item in enumerate(line_items))
                    xml_parts.append(f'    <Birim>{first_item.get("unit", "Adet")}</Birim>')
                    xml_parts.append(f'    <Miktar>{int(total_quantity)}</Miktar>')
                else:
                    xml_parts.append('    <Birim>Adet</Birim>')
                    xml_parts.append('    <Miktar>1</Miktar>')
            else:
                # Default values if no line items
                xml_parts.append('    <Mal_Hizmet_Adı>Mal/Hizmet</Mal_Hizmet_Adı>')
                xml_parts.append('    <KDV_Oranı>20</KDV_Oranı>')
                xml_parts.append('    <KDV_Tutarı>0,00 TL</KDV_Tutarı>')
                xml_parts.append('    <Mal_Hizmet_Toplam_Tutarı>0,00 TL</Mal_Hizmet_Toplam_Tutarı>')
                xml_parts.append('    <Vergiler_Dahil_Toplam_Tutar>0,00 TL</Vergiler_Dahil_Toplam_Tutar>')
                xml_parts.append('    <Ödenecek_Tutar>0,00 TL</Ödenecek_Tutar>')
                xml_parts.append('    <Satır_Toplam_Tutarı>0,00 TL</Satır_Toplam_Tutarı>')
                xml_parts.append('    <Tüm_Mal_Hizmetler>Mal/Hizmet</Tüm_Mal_Hizmetler>')
                xml_parts.append('    <Fatura_Kalemleri></Fatura_Kalemleri>')
                xml_parts.append('    <İskonto_Oranı>0</İskonto_Oranı>')
                xml_parts.append('    <İskonto_Tutarı>0,00 TL</İskonto_Tutarı>')
                xml_parts.append('    <Hesaplanan_KDV>0,00 TL</Hesaplanan_KDV>')
                xml_parts.append('    <Diğer_Vergiler>0,00 TL</Diğer_Vergiler>')
                xml_parts.append('    <Birim>Adet</Birim>')
                xml_parts.append('    <Miktar>1</Miktar>')
            
            # Add file and processing information
            file_name = self.invoice_data.get('file_name', 'fatura.pdf')
            xml_parts.append(f'    <Dosya_Adı>{self._escape_xml(file_name)}</Dosya_Adı>')
            xml_parts.append(f'    <İşlem_Tarihi>{current_time}</İşlem_Tarihi>')
            
            # Close invoice and root elements
            xml_parts.append('  </Fatura>')
            xml_parts.append('</E-Fatura_Verileri>')
            
            # Join all parts to create the XML string
            xml_string = '\n'.join(xml_parts)
            
            return xml_string
            
        except Exception as e:
            logger.error(f"Error converting to XML: {str(e)}")
            raise
    
    def _escape_xml(self, text):
        """Escape XML special characters"""
        if not text:
            return ""
        
        text = str(text)
        text = text.replace("&", "&amp;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        text = text.replace("\"", "&quot;")
        text = text.replace("'", "&apos;")
        return text
    
    def _format_date(self, date_str):
        """Keep date exactly as provided on the invoice"""
        if not date_str:
            return ""  # Leave empty if no date found
        
        # Return the date exactly as it appears on the invoice
        return str(date_str).strip()
    
    def _format_date_turkish(self, date_str):
        """Format date in Turkish format (DD-MM-YYYY)"""
        if not date_str:
            return datetime.now().strftime("%d-%m-%Y")
        
        try:
            # Try to parse various date formats and convert to DD-MM-YYYY
            date_str = str(date_str).strip()
            
            # If already in DD-MM-YYYY format, return as is
            if re.match(r'\d{2}-\d{2}-\d{4}', date_str):
                return date_str
            
            # If in YYYY-MM-DD format, convert to DD-MM-YYYY
            if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                year, month, day = date_str.split('-')
                return f"{day}-{month}-{year}"
            
            # If in DD/MM/YYYY format, convert to DD-MM-YYYY
            if re.match(r'\d{2}/\d{2}/\d{4}', date_str):
                return date_str.replace('/', '-')
            
            # If in YYYY/MM/DD format, convert to DD-MM-YYYY
            if re.match(r'\d{4}/\d{2}/\d{2}', date_str):
                year, month, day = date_str.split('/')
                return f"{day}-{month}-{year}"
            
            # If in DD.MM.YYYY format, convert to DD-MM-YYYY
            if re.match(r'\d{2}\.\d{2}\.\d{4}', date_str):
                return date_str.replace('.', '-')
            
            # If in YYYY.MM.DD format, convert to DD-MM-YYYY
            if re.match(r'\d{4}\.\d{2}\.\d{2}', date_str):
                year, month, day = date_str.split('.')
                return f"{day}-{month}-{year}"
            
            # If we can't parse it, return current date
            return datetime.now().strftime("%d-%m-%Y")
            
        except Exception as e:
            logger.warning(f"Could not parse date '{date_str}': {e}")
            return datetime.now().strftime("%d-%m-%Y")
    
    def _extract_numeric_value(self, value_str):
        """Extract numeric value from string that may contain units or other text"""
        if not value_str:
            return 1.0
        
        value_str = str(value_str).strip()
        
        # Remove common unit words
        value_str = value_str.replace('Adet', '').replace('adet', '').replace('ADET', '')
        value_str = value_str.replace('Kg', '').replace('kg', '').replace('KG', '')
        value_str = value_str.replace('Lt', '').replace('lt', '').replace('LT', '')
        value_str = value_str.replace('M', '').replace('m', '')
        value_str = value_str.replace('TL', '').replace('tl', '')
        
        # Replace comma with dot for decimal
        value_str = value_str.replace(',', '.')
        
        # Extract only numeric characters and decimal point
        import re
        numeric_match = re.search(r'[\d.]+', value_str)
        if numeric_match:
            try:
                return float(numeric_match.group())
            except ValueError:
                return 1.0
        else:
            return 1.0

    def _format_amount_turkish(self, amount_str):
        """Format amount in Turkish format (e.g., 1.234,56)"""
        if not amount_str or str(amount_str).strip() == '':
            return "0,00"
        
        try:
            # Clean the string
            amount_str = str(amount_str).strip()
            
            # Convert to float first
            amount = float(amount_str.replace(',', '.').replace(' ', ''))
            
            # Format with Turkish number format
            formatted = f"{amount:,.2f}"
            
            # Replace comma with dot for thousands separator and dot with comma for decimal
            formatted = formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
            
            return formatted
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Could not format amount '{amount_str}': {e}")
            return "0,00"
    
    def _generate_uuid(self):
        """Generate a simple UUID-like string for the invoice"""
        # In a real system, you would use a proper UUID generator
        # For this example, we'll create a simple placeholder based on invoice number
        invoice_num = self.invoice_data.get('invoice_number', '')
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"{timestamp}"
    
    def _format_amount(self, amount_str):
        """Keep amount exactly as provided on the invoice"""
        if not amount_str:
            return ""

        # Return the amount exactly as it appears on the invoice
        return str(amount_str).strip()
    
    def _validate_line_item(self, item, line_number):
        """Validate and clean line item data to prevent field mapping errors"""
        logger.debug(f"Validating line item {line_number}: {item}")
        
        validated_item = {}
        
        # Description validation - CRITICAL: Ensure description is text, not a number or amount
        description = item.get('description', '')
        if description:
            description_str = str(description).strip()
            
            # Check if description looks like a number or amount (common error)
            if isinstance(description, (int, float)):
                logger.warning(f"Line {line_number}: Description is a number: '{description}'. Using default.")
                validated_item['description'] = f"Ürün {line_number}"
            elif isinstance(description, str):
                # Remove common currency symbols and check if it's just a number
                cleaned_desc = description_str.replace('TL', '').replace('₺', '').replace('$', '').replace('€', '').replace('£', '').strip()
                
                # Check if it's just a number (with or without decimal)
                if cleaned_desc.replace('.', '').replace(',', '').replace(' ', '').isdigit():
                    logger.warning(f"Line {line_number}: Description appears to be an amount: '{description}'. Using default.")
                    validated_item['description'] = f"Ürün {line_number}"
                # Check if it's a very short string that might be a price
                elif len(cleaned_desc) <= 10 and any(char.isdigit() for char in cleaned_desc) and not any(char.isalpha() for char in cleaned_desc):
                    logger.warning(f"Line {line_number}: Description appears to be a price: '{description}'. Using default.")
                    validated_item['description'] = f"Ürün {line_number}"
                else:
                    validated_item['description'] = description_str
            else:
                validated_item['description'] = f"Ürün {line_number}"
        else:
            logger.warning(f"Line {line_number}: Missing description, using default")
            validated_item['description'] = f"Ürün {line_number}"
        
        # Keep quantity exactly as provided
        quantity = item.get('quantity', '1')
        validated_item['quantity'] = str(quantity).strip() if quantity else '1'
        
        # Unit validation
        unit = item.get('unit', 'ADET')
        validated_item['unit'] = str(unit).strip() if unit else 'ADET'
        
        # Keep unit price exactly as provided, but provide default if empty
        unit_price = item.get('unit_price', '')
        validated_item['unit_price'] = str(unit_price).strip() if unit_price else '0'
        
        # Keep tax rate exactly as provided, but provide default if empty
        tax_rate = item.get('tax_rate', '')
        validated_item['tax_rate'] = str(tax_rate).strip() if tax_rate else '20'
        
        # Keep amount exactly as provided, but provide default if empty
        amount = item.get('amount', '')
        validated_item['amount'] = str(amount).strip() if amount else '0'
        
        # Do not calculate amounts - use only what's on the invoice
        
        # Keep fields empty if not found on invoice - no defaults
        # Only provide description if completely missing
        if not validated_item.get('description'):
            validated_item['description'] = f"Item {line_number}"
        
        logger.debug(f"Validated line item {line_number}: {validated_item}")
        return validated_item
    def _parse_vat_rate(self, vat_str, default_rate='18'):
        """
        Parse VAT rate from various formats and prevent absurd values
        
        Handles formats like:
        - "18%", "%18", "KDV %18", "VAT 18%", "Value Added Tax: 20%", etc.
        - Prevents absurd values like 510% from incorrect parsing
        
        Args:
            vat_str: The VAT string to parse
            default_rate: Default VAT rate to use if parsing fails (default: '18')
            
        Returns:
            A string representation of the VAT rate as a number (e.g., '18', '20', '8.5')
        """
        if not vat_str:
            return default_rate
        
        # Convert to string if not already
        vat_str = str(vat_str).strip()
        logger.debug(f"Parsing VAT from: '{vat_str}'")
        
        # First, try to find a percentage pattern
        percentage_patterns = [
            # Common VAT patterns with percentages
            r'(?:KDV|VAT|Tax)?\s*[:%=]?\s*(\d{1,2}(?:[.,]\d{1,2})?)\s*%',  # KDV: 18%, VAT: 18%, Tax: 18%
            r'(?:KDV|VAT|Tax)?\s*%\s*(\d{1,2}(?:[.,]\d{1,2})?)',  # KDV %18, VAT %18, %18
            r'(\d{1,2}(?:[.,]\d{1,2})?)\s*%',  # 18%, 8.5%
            r'%\s*(\d{1,2}(?:[.,]\d{1,2})?)',  # %18, %8.5
            r'(?:KDV|VAT|Tax)?\s*(?:rate|oran|oranı)?\s*[:%=]?\s*(\d{1,2}(?:[.,]\d{1,2})?)',  # KDV rate: 18, VAT rate: 18
            r'(?:KDV|VAT|Tax)?\s*(\d{1,2}(?:[.,]\d{1,2})?)'  # KDV 18, VAT 18, just 18
        ]
        
        for pattern in percentage_patterns:
            match = re.search(pattern, vat_str, re.IGNORECASE)
            if match:
                vat_value = match.group(1).replace(',', '.')
                try:
                    vat_float = float(vat_value)
                    # Sanity check - VAT rates are typically between 1-30%
                    if 1 <= vat_float <= 30:
                        logger.debug(f"Successfully parsed VAT rate '{vat_str}' as {vat_float}%")
                        return str(vat_float)
                    elif vat_float == 0:
                        logger.warning(f"Zero VAT rate detected, using default")
                        return default_rate
                    elif vat_float < 0:
                        logger.warning(f"Negative VAT rate detected, using default")
                        return default_rate
                    elif vat_float > 30:
                        # For very high values like 510%, default to standard rate
                        if vat_float >= 100:
                            logger.warning(f"Parsed VAT rate '{vat_str}' as {vat_float}%, which is absurd. Using default.")
                            return default_rate
                        # Check if it's a common error case that can be corrected (only for values 31-99)
                        elif 31 <= vat_float < 100:
                            logger.warning(f"Parsed VAT rate '{vat_str}' as {vat_float}%, which seems too high. Using default.")
                            return default_rate
                        else:
                            logger.warning(f"Parsed VAT rate '{vat_str}' as {vat_float}%, which seems unreasonable. Using default.")
                            return default_rate
                except ValueError:
                    logger.warning(f"Failed to convert matched VAT value '{vat_value}' to float")
        
        # If we get here, try a more generic approach with number cleaning
        cleaned_vat = self._clean_number(vat_str.replace('%', ''))
        
        try:
            vat_float = float(cleaned_vat)
            
            # Handle common parsing errors
            if vat_float > 100:
                # Could be a case where "18%" was parsed as 1800 (percentage sign treated as 00)
                if 1000 <= vat_float <= 3000:
                    corrected = vat_float / 100
                    logger.info(f"Correcting likely VAT parsing error: {vat_float}% -> {corrected}%")
                    return str(corrected)
                # Could be a case where "18" was parsed as 180 (extra 0 added)
                elif 100 <= vat_float < 1000:
                    corrected = vat_float / 10
                    logger.info(f"Correcting likely VAT parsing error: {vat_float}% -> {corrected}%")
                    return str(corrected)
                # Could be a case where "18" was parsed as 1800 (two extra 0s added)
                elif vat_float >= 1000:
                    possible_correction = vat_float / 100
                    if possible_correction <= 30:  # Common VAT range
                        logger.info(f"Correcting likely VAT parsing error: {vat_float}% -> {possible_correction}%")
                        return str(possible_correction)
                    else:
                        logger.warning(f"VAT rate '{vat_str}' parsed as {vat_float}% is out of reasonable range, using default")
                        return default_rate
                else:
                    logger.warning(f"VAT rate '{vat_str}' parsed as {vat_float}% is out of reasonable range, using default")
                    return default_rate
            elif vat_float <= 0:
                logger.warning(f"VAT rate '{vat_str}' parsed as {vat_float}% is non-positive, using default")
                return default_rate
            else:
                # Final sanity check
                if vat_float > 30:
                    logger.warning(f"VAT rate '{vat_str}' parsed as {vat_float}% is unusually high, using default")
                    return default_rate
                elif 1 <= vat_float <= 30:
                    return str(vat_float)
                else:
                    # Edge case: 0 < vat_float < 1
                    logger.warning(f"VAT rate '{vat_str}' parsed as {vat_float}% is too low, using default")
                    return default_rate
        except ValueError:
            logger.warning(f"Could not parse VAT rate '{vat_str}', using default")
            return default_rate
    
    def _clean_number(self, number_str):
        """Clean and standardize Turkish number format (same as PDFExtractor)"""
        if not number_str:
            return '0'
        
        # Convert to string if not already
        number_str = str(number_str).strip()
        
        # Remove currency symbols
        number_str = number_str.replace('₺', '').replace('TL', '').replace('$', '').replace('€', '').strip()
        
        # Handle Turkish number format: 15.000,00 (thousands separator = dot, decimal = comma)
        if '.' in number_str and ',' in number_str:
            # Pattern: 15.000,00 or 1.234.567,89
            parts = number_str.split(',')
            if len(parts) == 2 and len(parts[1]) <= 2:  # Valid decimal part
                # Remove thousand separators (dots) from integer part
                integer_part = parts[0].replace('.', '')
                decimal_part = parts[1]
                number_str = f"{integer_part}.{decimal_part}"
            else:
                # Just replace comma with dot
                number_str = number_str.replace(',', '.')
        elif ',' in number_str and '.' not in number_str:
            # Pattern: 1234,56 (only decimal comma)
            number_str = number_str.replace(',', '.')
        elif '.' in number_str and ',' not in number_str:
            # Check if it's likely a thousands separator or decimal point
            dot_pos = number_str.rfind('.')
            after_dot = number_str[dot_pos+1:]
            if len(after_dot) == 3 and after_dot.isdigit():
                # Likely thousands separator: 15.000 -> 15000
                number_str = number_str.replace('.', '')
            # else: assume decimal point
        
        # Remove any remaining non-numeric characters except dots
        cleaned = re.sub(r'[^\d.]', '', number_str)
        
        # Handle multiple decimal points (keep only the last one)
        if cleaned.count('.') > 1:
            parts = cleaned.split('.')
            cleaned = ''.join(parts[:-1]) + '.' + parts[-1]
        
        # Ensure we have a valid number
        try:
            float_val = float(cleaned)
            return str(float_val)  # Normalize format with dot as decimal separator
        except ValueError:
            logger.warning(f"Could not parse number '{number_str}' -> '{cleaned}'")
            return '0'
