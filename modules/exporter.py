import pandas as pd
from datetime import datetime
from pymongo import MongoClient
from typing import List, Dict, Any, Optional
from utils.logger import logger
import os

class Exporter:
    def __init__(self, mongodb_uri: Optional[str] = None):
        self.mongodb_uri = mongodb_uri

    def export_to_csv(self, leads: List[Dict[str, Any]], location: str) -> str:
        """Export leads to a deduplicated CSV file."""
        if not leads:
            logger.warning("No leads to export.")
            return ""

        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"leads_{date_str}_{location.replace(' ', '_').lower()}.csv"
        filepath = os.path.join("data", filename)
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        df = pd.DataFrame(leads)
        # Select and order columns
        columns = [
            'business_name', 'category', 'email', 'phone', 'website', 
            'social_links', 'address', 'city', 'lead_score', 'quality_tier', 'source'
        ]
        # Filter existing columns
        cols_to_use = [col for col in columns if col in df.columns]
        df = df[cols_to_use]
        
        # Convert social_links list to string for CSV
        if 'social_links' in df.columns:
            df['social_links'] = df['social_links'].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
        
        df.to_csv(filepath, index=False)
        logger.info(f"Leads exported to CSV: {filepath}")
        return filepath

    def export_to_mongodb(self, leads: List[Dict[str, Any]]):
        """Export leads to MongoDB Atlas if URI is provided."""
        if not self.mongodb_uri:
            return

        try:
            client = MongoClient(self.mongodb_uri)
            db = client.lead_generation
            collection = db.leads
            
            # Insert many but handle duplicates or updates
            for lead in leads:
                collection.update_one(
                    {'business_name': lead['business_name'], 'address': lead.get('address')},
                    {'$set': lead},
                    upsert=True
                )
            logger.info("Leads successfully synced to MongoDB Atlas.")
        except Exception as e:
            logger.error(f"Error exporting to MongoDB: {e}")
