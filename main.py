import argparse
import sys
from tqdm import tqdm
from config import Config
from utils.logger import logger
from modules.business_discovery import BusinessDiscovery
from modules.website_crawler import WebsiteCrawler
from modules.contact_extractor import ContactExtractor
from modules.llm_extractor import LLMExtractor
from modules.lead_processor import LeadProcessor
from modules.exporter import Exporter

def run_pipeline(location: str, radius: int, category: str, limit: int = 50):
    """Orchestrate the lead generation pipeline."""
    try:
        # Validate Config
        Config.validate()
        
        # Initialize Modules
        discovery_module = BusinessDiscovery(Config.GOOGLE_MAPS_API_KEY)
        crawler_module = WebsiteCrawler()
        regex_extractor = ContactExtractor()
        llm_extractor = LLMExtractor(Config.GEMINI_API_KEY)
        processor_module = LeadProcessor()
        exporter_module = Exporter(Config.MONGODB_URI)
        
        # Step 1: Discovery
        logger.info(f"Starting discovery for {category} in {location} (Limit: {limit})...")
        raw_businesses = discovery_module.search_businesses(location, radius, category, max_results=limit)
        
        if not raw_businesses:
            logger.warning("No businesses found matching the criteria.")
            return

        logger.info(f"Found {len(raw_businesses)} potential businesses.")
        
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        # Step 2: Crawling and Extraction (Parallelized)
        processed_leads = []
        
        def process_business(biz):
            """Helper to process a single business lead."""
            try:
                website = biz.get('website')
                biz['social_links'] = [] # Initialize
                biz['source'] = "Google Maps" # Default source
                
                if website:
                    crawl_results = crawler_module.crawl(website)
                    
                    # Check if crawling failed or returned empty content
                    homepage_text = crawl_results.get('homepage_text', "")
                    contact_text = crawl_results.get('contact_page_text', "")
                    
                    if not crawl_results or (not homepage_text and not contact_text):
                        logger.warning(f"No content found for {biz.get('name')} at {website}. Skipping extraction.")
                        biz['source'] = "Crawl Error: No content found"
                        return biz

                    biz['social_links'] = crawl_results.get('social_links', [])
                    
                    # Regex Extraction
                    extracted_data = regex_extractor.extract(homepage_text + " " + contact_text)
                    
                    # Populate business object
                    found_via_regex = False
                    if extracted_data['emails']:
                        biz['email'] = extracted_data['emails'][0]
                        found_via_regex = True
                    else:
                        biz['email'] = None

                    if extracted_data['phones']:
                        biz['phone'] = extracted_data['phones'][0]
                        found_via_regex = True
                    else:
                        biz['phone'] = None

                    if found_via_regex:
                        biz['source'] = "crawling"

                    # Step 3: LLM Fallback if basic extraction fails
                    if not biz['email'] or not biz['phone']:
                        combined_text = (homepage_text + " " + contact_text)[:3000]
                        llm_data = llm_extractor.extract_structured_data(combined_text)
                        
                        if llm_data:
                            if not biz['email'] and llm_data.get('email'):
                                biz['email'] = llm_data.get('email')
                                biz['source'] = "llm_fallback"
                            if not biz['phone'] and llm_data.get('phone'):
                                biz['phone'] = llm_data.get('phone')
                                biz['source'] = "llm_fallback"
                                
                            # Override business name or address only if they are significantly better
                            if not biz.get('address') and llm_data.get('address'):
                                biz['address'] = llm_data.get('address')
                
                return biz
            except Exception as e:
                logger.error(f"Error processing business {biz.get('name', 'Unknown')}: {e}")
                return biz

        logger.info(f"Processing {len(raw_businesses)} businesses in parallel (max_workers=5)...")
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_biz = {executor.submit(process_business, biz): biz for biz in raw_businesses}
            
            for future in tqdm(as_completed(future_to_biz), total=len(raw_businesses), desc="Processing Businesses"):
                try:
                    result_biz = future.result()
                    processed_leads.append(result_biz)
                except Exception as e:
                    logger.error(f"Error in future result: {e}")

        # Step 4: Processing (Scoring and Deduplication)
        final_leads = processor_module.process_leads(processed_leads)
        
        # Step 5: Exporting
        csv_path = exporter_module.export_to_csv(final_leads, location)
        exporter_module.export_to_mongodb(final_leads)
        
        logger.info(f"Pipeline completed successfully. {len(final_leads)} leads generated.")
        print(f"\n[SUCCESS] Generated {len(final_leads)} leads.")
        print(f"[SUCCESS] CSV Output: {csv_path}")

    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI-Powered Hyperlocal Business Lead Generation Tool")
    parser.add_argument("--location", type=str, required=True, help="City name, postcode, or lat/lng")
    parser.add_argument("--radius", type=int, default=5, help="Search radius in km (1-25)")
    parser.add_argument("--category", type=str, default="restaurant", help="Business category (cafe, retail, etc.)")
    parser.add_argument("--limit", type=int, default=30, help="Maximum number of businesses to fetch (default: 50)")
    
    args = parser.parse_args()
    run_pipeline(args.location, args.radius, args.category, args.limit)
