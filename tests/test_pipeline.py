import unittest
from unittest.mock import MagicMock, patch
from modules.business_discovery import BusinessDiscovery
from modules.contact_extractor import ContactExtractor
from modules.lead_processor import LeadProcessor
from utils.helpers import calculate_lead_score

class TestLeadGenPipeline(unittest.TestCase):
    def setUp(self):
        self.extractor = ContactExtractor()
        self.processor = LeadProcessor()

    def test_contact_extraction(self):
        text = "Contact us at info@example.com or call +44 20 1234 5678"
        results = self.extractor.extract(text)
        self.assertIn("info@example.com", results['emails'])
        self.assertIn("+44 20 1234 5678", results['phones'])

    def test_lead_scoring(self):
        lead = {
            "website": "http://example.com",
            "email": "info@example.com",
            "phone": "+44 20 1234 5678"
        }
        score = calculate_lead_score(lead)
        # 3 (website) + 3 (email) + 2 (phone) = 8
        self.assertEqual(score, 8)

    def test_deduplication(self):
        leads = [
            {"business_name": "Test Biz", "address": "123 Lane", "lead_score": 5},
            {"business_name": "test biz", "address": "123 lane ", "lead_score": 8}
        ]
        deduplicated = self.processor._deduplicate(leads)
        self.assertEqual(len(deduplicated), 1)
        self.assertEqual(deduplicated[0]['lead_score'], 8)

if __name__ == '__main__':
    unittest.main()
