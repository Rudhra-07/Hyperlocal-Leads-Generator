import re
from typing import Dict, List, Optional
from utils.validators import is_valid_email, is_valid_phone
from utils.logger import logger

class ContactExtractor:
    def __init__(self):
        # Email patterns
        self.email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        
        # Phone patterns (International & Local)
        # Matches: +44 20 7946 0958, 020 1234 5678, +1 (555) 123-4567, 07123 456789
        # Uses non-capturing groups so re.findall returns the entire matched phone number.
        self.phone_pattern = r'(?:\+?\d{1,4}[\s-]?)?(?:\(?\d{3}\)?[\s-]?)?[\d\s-]{7,15}'

    def extract(self, text: str) -> Dict[str, List[str]]:
        """Extract emails and phones from text using regex."""
        if not text:
            return {'emails': [], 'phones': []}

        # Extract emails
        emails = re.findall(self.email_pattern, text)
        valid_emails = list(set([e.lower() for e in emails if is_valid_email(e)]))
        
        # Prioritize specific email prefixes
        priority_prefixes = ['info@', 'hello@', 'contact@', 'support@', 'admin@']
        valid_emails.sort(key=lambda x: any(prefix in x for prefix in priority_prefixes), reverse=True)

        # Extract phones
        phones = re.findall(self.phone_pattern, text)
        # Cleanup: phones returned by findall might be tuples if there are capturing groups
        cleaned_phones = []
        for p in phones:
            if isinstance(p, tuple):
                p = "".join(p)
            # Remove whitespace and basic cleaning
            p_clean = p.strip()
            if len(p_clean) >= 7 and is_valid_phone(p_clean):
                cleaned_phones.append(p_clean)
        
        valid_phones = list(set(cleaned_phones))

        return {
            'emails': valid_emails,
            'phones': valid_phones
        }

    def merge_results(self, results_list: List[Dict[str, List[str]]]) -> Dict[str, List[str]]:
        """Merge multiple extraction results and deduplicate."""
        all_emails = set()
        all_phones = set()
        
        for res in results_list:
            all_emails.update(res.get('emails', []))
            all_phones.update(res.get('phones', []))
            
        return {
            'emails': list(all_emails),
            'phones': list(all_phones)
        }
