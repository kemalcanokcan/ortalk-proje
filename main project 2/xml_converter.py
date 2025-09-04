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
        """Convert invoice data to UBL-TR format XML"""
        try:
            # Create XML string directly
            xml_parts = []
            xml_parts.append('<?xml version="1.0" encoding="UTF-8"?>')
            xml_parts.append('<Invoice>')
            
            # Add invoice number
            invoice_number = self.invoice_data.get('invoice_number', '')
            if not invoice_number:
                logger.warning("Missing invoice number, using placeholder")
                invoice_number = f"INV-{self._generate_uuid()}"
            xml_parts.append(f'  <InvoiceNumber>{self._escape_xml(invoice_number)}</InvoiceNumber>')
            
            # Add issue date in ISO format (YYYY-MM-DD)
            issue_date = self.invoice_data.get('invoice_date', '')
            formatted_date = self._format_date(issue_date)
            xml_parts.append(f'  <IssueDate>{formatted_date}</IssueDate>')
            
            # Add seller information
            xml_parts.append('  <Seller>')
            
            # Seller name (required)
            seller_name = self.invoice_data.get('vendor_name', '')
            if not seller_name:
                logger.warning("Missing seller name, using placeholder")
                seller_name = "Unknown Seller"
            xml_parts.append(f'    <Name>{self._escape_xml(seller_name)}</Name>')
            
            # Seller VKN (tax ID)
            seller_vkn = self.invoice_data.get('vendor_tax_id', '')
            if not seller_vkn:
                logger.warning("Missing seller VKN (tax ID)")
            xml_parts.append(f'    <VKN>{self._escape_xml(seller_vkn)}</VKN>')
            xml_parts.append('  </Seller>')
            
            # Add buyer information
            xml_parts.append('  <Buyer>')
            
            # Buyer name (required)
            buyer_name = self.invoice_data.get('customer_name', '')
            if not buyer_name:
                logger.warning("Missing buyer name, using placeholder")
                buyer_name = "Unknown Buyer"
            xml_parts.append(f'    <Name>{self._escape_xml(buyer_name)}</Name>')
            
            # Buyer VKN (tax ID)
            buyer_vkn = self.invoice_data.get('customer_tax_id', '')
            if not buyer_vkn:
                logger.warning("Missing buyer VKN (tax ID)")
            xml_parts.append(f'    <VKN>{self._escape_xml(buyer_vkn)}</VKN>')
            xml_parts.append('  </Buyer>')
            
            # Add line items
            xml_parts.append('  <Items>')
            
            # Process each line item
            for i, item in enumerate(self.invoice_data.get('line_items', []), 1):
                logger.debug(f"Processing line item {i}: {item}")
                
                # Validate item data before XML creation
                validated_item = self._validate_line_item(item, i)
                
                # Create item element
                xml_parts.append('    <Item>')
                
                # Description (required)
                item_description = validated_item.get('description', f'Item {i}')
                xml_parts.append(f'      <Description>{self._escape_xml(str(item_description))}</Description>')
                
                # Quantity (required)
                quantity = self._format_amount(validated_item.get('quantity', '1'))
                xml_parts.append(f'      <Quantity>{quantity}</Quantity>')
                
                # Unit price (required)
                unit_price = self._format_amount(validated_item.get('unit_price', '0'))
                xml_parts.append(f'      <UnitPrice>{unit_price}</UnitPrice>')
                
                # VAT rate (required)
                vat_rate = validated_item.get('tax_rate', '18')
                xml_parts.append(f'      <VAT>{vat_rate}</VAT>')
                
                # Total amount for this item (required)
                total = self._format_amount(validated_item.get('amount', '0'))
                xml_parts.append(f'      <Total>{total}</Total>')
                
                xml_parts.append('    </Item>')
                
                logger.info(f"Added line item {i}: '{item_description}' - {quantity} x {unit_price} = {total}")
            
            xml_parts.append('  </Items>')
            
            # Add total amount exactly as on invoice
            total_amount = self._format_amount(self.invoice_data.get('total_amount', ''))
            xml_parts.append(f'  <TotalAmount>{total_amount}</TotalAmount>')
            
            # Add currency exactly as found on invoice
            currency = self.invoice_data.get('currency', '')  # Leave empty if not found
            xml_parts.append(f'  <Currency>{currency}</Currency>')
            
            xml_parts.append('</Invoice>')
            
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
        
        # Description validation - CRITICAL: Ensure description is text, not a number
        description = item.get('description', '')
        if description:
            # Check if description looks like a number (common error)
            if isinstance(description, (int, float)) or (isinstance(description, str) and description.replace('.', '').replace(',', '').isdigit()):
                logger.warning(f"Line {line_number}: Description appears to be a number: '{description}'. Using default.")
                validated_item['description'] = f"Ürün {line_number}"
            else:
                validated_item['description'] = str(description).strip()
        else:
            logger.warning(f"Line {line_number}: Missing description, using default")
            validated_item['description'] = f"Ürün {line_number}"
        
        # Keep quantity exactly as provided
        quantity = item.get('quantity', '1')
        validated_item['quantity'] = str(quantity).strip() if quantity else '1'
        
        # Unit validation
        unit = item.get('unit', 'ADET')
        validated_item['unit'] = str(unit).strip() if unit else 'ADET'
        
        # Keep unit price exactly as provided
        unit_price = item.get('unit_price', '')
        validated_item['unit_price'] = str(unit_price).strip() if unit_price else ''
        
        # Keep tax rate exactly as provided - no parsing or validation
        tax_rate = item.get('tax_rate', '')
        validated_item['tax_rate'] = str(tax_rate).strip() if tax_rate else ''
        
        # Keep amount exactly as provided
        amount = item.get('amount', '')
        validated_item['amount'] = str(amount).strip() if amount else ''
        
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
