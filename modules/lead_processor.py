from typing import List, Dict, Any
import pandas as pd
from utils.helpers import calculate_lead_score, get_quality_tier, normalize_string
from utils.logger import logger

class LeadProcessor:
    def process_leads(self, raw_leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process leads: Score, Tier, and Deduplicate."""
        if not raw_leads:
            return []

        scored_leads = []
        for lead in raw_leads:
            score = calculate_lead_score(lead)
            lead['lead_score'] = score
            lead['quality_tier'] = get_quality_tier(score)
            scored_leads.append(lead)

        # Deduplication logic
        deduplicated = self._deduplicate(scored_leads)
        
        # Sort by score descending
        deduplicated.sort(key=lambda x: x['lead_score'], reverse=True)
        
        return deduplicated

    def _deduplicate(self, leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicates based on normalized business name and address/phone."""
        seen = {}
        unique_leads = []
        
        for lead in leads:
            name_norm = normalize_string(lead.get('business_name', ''))
            phone_norm = normalize_string(lead.get('phone', ''))
            address_norm = normalize_string(lead.get('address', ''))
            
            # Key for deduplication
            key = f"{name_norm}|{phone_norm if phone_norm else address_norm}"
            
            if key not in seen:
                seen[key] = lead
            else:
                # Keep the one with the higher score
                if lead['lead_score'] > seen[key]['lead_score']:
                    seen[key] = lead
                    
        return list(seen.values())
