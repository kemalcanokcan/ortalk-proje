import pdfplumber
import re
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFExtractor:
    def __init__(self, pdf_path):
        """Initialize the PDF extractor with the path to the PDF file"""
        self.pdf_path = pdf_path
        self.text_content = ""
        self.tables = []
        
    def extract_all_text(self):
        """Extract all text content from the PDF"""
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                if not pdf.pages:
                    logger.warning("PDF has no pages")
                    return ""
                
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        self.text_content += page_text + "\n"
                    else:
                        logger.warning(f"No text found on page {page.page_number}")
                        
            if not self.text_content.strip():
                logger.warning("No text content extracted from PDF")
                
            return self.text_content
        except FileNotFoundError:
            logger.error(f"PDF file not found: {self.pdf_path}")
            raise FileNotFoundError("PDF dosyası bulunamadı")
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise Exception(f"PDF'den metin çıkarılırken hata oluştu: {str(e)}")
    
    def extract_tables(self):
        """Extract tables from the PDF"""
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                if not pdf.pages:
                    logger.warning("PDF has no pages for table extraction")
                    return []
                
                for page in pdf.pages:
                    try:
                        tables = page.extract_tables()
                        if tables:
                            self.tables.extend(tables)
                            logger.info(f"Found {len(tables)} table(s) on page {page.page_number}")
                        else:
                            logger.debug(f"No tables found on page {page.page_number}")
                    except Exception as page_error:
                        logger.warning(f"Error extracting tables from page {page.page_number}: {str(page_error)}")
                        continue
                        
            logger.info(f"Total tables extracted: {len(self.tables)}")
            return self.tables
        except FileNotFoundError:
            logger.error(f"PDF file not found: {self.pdf_path}")
            raise FileNotFoundError("PDF dosyası bulunamadı")
        except Exception as e:
            logger.error(f"Error extracting tables from PDF: {str(e)}")
            raise Exception(f"PDF'den tablo çıkarılırken hata oluştu: {str(e)}")
    
    def extract_invoice_data(self):
        """Extract structured invoice data from the PDF"""
        try:
            logger.info("Starting invoice data extraction")
            
            # Extract all text if not already done
            if not self.text_content:
                self.extract_all_text()
            
            # Extract tables if not already done
            if not self.tables:
                self.extract_tables()
            
            # Validate that we have some content to work with
            if not self.text_content.strip():
                logger.warning("No text content available for extraction")
                raise ValueError("PDF'den metin içeriği çıkarılamadı. Dosya boş veya okunamıyor olabilir.")
            
            # Initialize invoice data dictionary
            invoice_data = {
                'invoice_number': '',
                'invoice_date': '',
                'vendor_name': '',
                'vendor_tax_id': '',
                'vendor_address': '',
                'customer_name': '',
                'customer_tax_id': '',
                'customer_address': '',
                'line_items': [],
                'subtotal': '',
                'tax_amount': '',
                'total_amount': '',
                'notes': ''
            }
            
            # Extract invoice number
            invoice_number_match = re.search(r'Fatura No\s*:\s*([A-Za-z0-9-]+)', self.text_content)
            if invoice_number_match:
                invoice_data['invoice_number'] = invoice_number_match.group(1)
            
            # Extract invoice date
            date_match = re.search(r'Fatura Tarihi\s*:\s*(\d{1,2}[./]\d{1,2}[./]\d{4})', self.text_content)
            if date_match:
                invoice_data['invoice_date'] = date_match.group(1)
                
                # Try to convert to standard date format
                try:
                    date_str = date_match.group(1)
                    # Handle different date formats
                    if '.' in date_str:
                        day, month, year = date_str.split('.')
                    elif '/' in date_str:
                        day, month, year = date_str.split('/')
                    
                    # Ensure year has 4 digits
                    if len(year) == 2:
                        year = '20' + year
                    
                    # Format as ISO date
                    invoice_data['invoice_date_iso'] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                except:
                    # Keep original format if parsing fails
                    pass
            
            # Extract vendor information
            vendor_section = re.search(r'SATICI\s*\n(.*?)(?=ALICI|\Z)', self.text_content, re.DOTALL)
            if vendor_section:
                vendor_text = vendor_section.group(1)
                
                # Extract vendor name
                vendor_name_match = re.search(r'^(.*?)(?=\n|VKN|$)', vendor_text)
                if vendor_name_match:
                    invoice_data['vendor_name'] = vendor_name_match.group(1).strip()
                
                # Extract vendor tax ID
                vendor_tax_match = re.search(r'VKN\s*:\s*(\d+)', vendor_text)
                if vendor_tax_match:
                    invoice_data['vendor_tax_id'] = vendor_tax_match.group(1)
                
                # Extract vendor address
                address_lines = []
                for line in vendor_text.split('\n'):
                    if not re.search(r'(VKN|Tel|E-Posta|Fax)', line) and line.strip():
                        if line.strip() != invoice_data['vendor_name']:
                            address_lines.append(line.strip())
                
                invoice_data['vendor_address'] = ' '.join(address_lines)
            
            # Extract customer information
            customer_section = re.search(r'ALICI\s*\n(.*?)(?=\n\s*Malzeme|MALIN|$)', self.text_content, re.DOTALL)
            if customer_section:
                customer_text = customer_section.group(1)
                
                # Extract customer name
                customer_name_match = re.search(r'^(.*?)(?=\n|VKN|$)', customer_text)
                if customer_name_match:
                    invoice_data['customer_name'] = customer_name_match.group(1).strip()
                
                # Extract customer tax ID
                customer_tax_match = re.search(r'VKN\s*:\s*(\d+)', customer_text)
                if customer_tax_match:
                    invoice_data['customer_tax_id'] = customer_tax_match.group(1)
                
                # Extract customer address
                address_lines = []
                for line in customer_text.split('\n'):
                    if not re.search(r'(VKN|Tel|E-Posta|Fax)', line) and line.strip():
                        if line.strip() != invoice_data['customer_name']:
                            address_lines.append(line.strip())
                
                invoice_data['customer_address'] = ' '.join(address_lines)
            
            # Try to extract line items from tables first
            if self.tables:
                for table in self.tables:
                    # Check if this looks like an invoice items table
                    if table and len(table) > 1:
                        header = table[0]
                        # Check if header contains typical invoice item columns
                        header_text = ' '.join([str(cell) for cell in header if cell])
                        if re.search(r'(Malzeme|Hizmet|Miktar|Birim|Fiyat|Tutar|KDV)', header_text):
                            # Process rows after header
                            for row in table[1:]:
                                if all(cell is None or cell.strip() == '' for cell in row):
                                    continue  # Skip empty rows
                                
                                # Try to extract item data
                                item = {}
                                
                                # Map columns based on header
                                col_map = {}
                                for i, col_name in enumerate(header):
                                    if col_name:
                                        col_name = str(col_name).lower()
                                        if any(term in col_name for term in ['malzeme', 'hizmet', 'açıklama']):
                                            col_map['description'] = i
                                        elif any(term in col_name for term in ['miktar']):
                                            col_map['quantity'] = i
                                        elif any(term in col_name for term in ['birim']):
                                            col_map['unit'] = i
                                        elif any(term in col_name for term in ['fiyat']):
                                            col_map['unit_price'] = i
                                        elif any(term in col_name for term in ['kdv', 'vergi']):
                                            col_map['tax_rate'] = i
                                        elif any(term in col_name for term in ['tutar', 'toplam']):
                                            col_map['amount'] = i
                                
                                # Extract data based on column mapping
                                for field, index in col_map.items():
                                    if index < len(row) and row[index]:
                                        item[field] = str(row[index]).strip()
                                
                                # Only add if we have at least description and amount
                                if 'description' in item and item['description'] and (
                                    'amount' in item or 'quantity' in item):
                                    invoice_data['line_items'].append(item)
            
            # If no line items found in tables, try text-based extraction
            if not invoice_data['line_items']:
                items_section = re.search(r'(Malzeme / Hizmet.*?)(?=Vergiler|Toplam|Yalnız|$)', 
                                         self.text_content, re.DOTALL)
                if items_section:
                    items_text = items_section.group(1)
                    lines = items_text.strip().split('\n')
                    
                    # Skip header line
                    header_found = False
                    
                    for line in lines:
                        if re.search(r'Malzeme / Hizmet|Miktar|Birim Fiyat|KDV|Tutar', line):
                            header_found = True
                            continue
                        
                        if header_found and line.strip():
                            # Try to match line item pattern
                            item_match = re.search(r'^(.*?)\s+(\d+(?:,\d+)?)\s+(\w+)\s+(\d+(?:,\d+)?)\s+%(\d+)\s+(\d+(?:,\d+)?)', line)
                            if item_match:
                                item = {
                                    'description': item_match.group(1).strip(),
                                    'quantity': item_match.group(2),
                                    'unit': item_match.group(3),
                                    'unit_price': item_match.group(4),
                                    'tax_rate': item_match.group(5),
                                    'amount': item_match.group(6)
                                }
                                invoice_data['line_items'].append(item)
                            else:
                                # This might be a continuation of the previous item description
                                if invoice_data['line_items'] and line.strip():
                                    invoice_data['line_items'][-1]['description'] += ' ' + line.strip()
            
            # Extract totals
            subtotal_match = re.search(r'Mal Hizmet Toplam Tutarı\s*:\s*([0-9.,]+)', self.text_content)
            if subtotal_match:
                invoice_data['subtotal'] = subtotal_match.group(1)
            
            tax_match = re.search(r'Hesaplanan KDV\s*:\s*([0-9.,]+)', self.text_content)
            if tax_match:
                invoice_data['tax_amount'] = tax_match.group(1)
            
            total_match = re.search(r'Vergiler Dahil Toplam Tutar\s*:\s*([0-9.,]+)', self.text_content)
            if total_match:
                invoice_data['total_amount'] = total_match.group(1)
            
            # Check for withholding tax (tevkifat)
            withholding_match = re.search(r'Tevkifat\s*:\s*([0-9.,]+)', self.text_content)
            if withholding_match:
                invoice_data['withholding_tax'] = withholding_match.group(1)
            
            # Extract notes or additional information
            notes_match = re.search(r'Not\s*:(.*?)(?=\Z)', self.text_content, re.DOTALL)
            if notes_match:
                invoice_data['notes'] = notes_match.group(1).strip()
            
            logger.info("Invoice data extraction completed successfully")
            return invoice_data
            
        except ValueError as ve:
            logger.error(f"Validation error during invoice extraction: {str(ve)}")
            raise ve
        except Exception as e:
            logger.error(f"Unexpected error during invoice data extraction: {str(e)}")
            raise Exception(f"Fatura verisi çıkarılırken beklenmeyen hata oluştu: {str(e)}")
