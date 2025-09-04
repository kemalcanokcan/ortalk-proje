import re
import logging

logger = logging.getLogger(__name__)

class AddressParser:
    """Parses unstructured Turkish addresses into structured components."""

    def __init__(self):
        # Pre-compile regex patterns for efficiency
        self.patterns = {
            'street': r'((?:[\w\sçğıöşüÇĞİÖŞÜ]+(?:\s+Caddesi|\s+Cad\.|\s+Cd\.|\s+Sokağı|\s+Sk\.|\s+Bulvarı|\s+Blv\.|\s+Yolu))[,\s]*)',
            'number': r'(?:No[:.]?\s*(\d+[A-Z]?)|(?:Bina\s*No|Dış\s*Kapı\s*No)[:.]?\s*(\d+[A-Z]?))',
            'district_city': r'([\wçğıöşüÇĞİÖŞÜ\s]+)/([\wçğıöşüÇĞİÖŞÜ\s]+)$'
        }

    def parse(self, address_text: str) -> dict:
        """Parses the address string and returns a dictionary of components."""
        if not address_text:
            return {}

        # Normalize and clean the address first
        cleaned_address = self._normalize(address_text)
        
        parsed_components = {
            'street': None,
            'house_number': None,
            'district': None,
            'city': None,
            'country': 'Turkey' # Assume Turkey
        }

        # 1. Extract District/City (e.g., "ÇANKAYA / ANKARA")
        match = re.search(self.patterns['district_city'], cleaned_address)
        if match:
            parsed_components['district'] = match.group(1).strip()
            parsed_components['city'] = match.group(2).strip()
            # Remove this part from the address to avoid re-matching
            cleaned_address = cleaned_address[:match.start()].strip()

        # 2. Extract House Number
        match = re.search(self.patterns['number'], cleaned_address, re.IGNORECASE)
        if match:
            # The pattern has two capturing groups, one will be None
            house_number = next((g for g in match.groups() if g is not None), None)
            if house_number:
                parsed_components['house_number'] = house_number.strip()
                cleaned_address = cleaned_address[:match.start()].strip()

        # 3. Extract Street
        # The remaining part is likely the street and neighborhood
        parsed_components['street'] = cleaned_address.strip()
        
        logger.info(f"Parsed address '{address_text}' into: {parsed_components}")
        return parsed_components

    def _normalize(self, address: str) -> str:
        """Normalizes common Turkish address abbreviations and cleans the string."""
        standardizations = {
            r'\b(Mah|Mh)\.?\b': 'Mahallesi',
            r'\b(Cad|Cd)\.?\b': 'Caddesi',
            r'\b(Sok|Sk)\.?\b': 'Sokağı',
            r'\b(Bul|Blv)\.?\b': 'Bulvarı',
            r'\b(Apt|Ap)\.?\b': 'Apartmanı',
            r'\bNo\.?\b': 'No'
        }
        normalized_address = address
        for pattern, replacement in standardizations.items():
            normalized_address = re.sub(pattern, replacement, normalized_address, flags=re.IGNORECASE)
        
        # Remove extra whitespace
        normalized_address = re.sub(r'\s+', ' ', normalized_address).strip()
        return normalized_address
