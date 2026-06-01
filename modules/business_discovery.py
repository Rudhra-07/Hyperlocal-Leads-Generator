import googlemaps
import requests
from typing import List, Dict, Any, Optional
from config import Config
from utils.logger import logger
from tenacity import retry, wait_fixed, stop_after_attempt
from geopy.geocoders import Nominatim

class BusinessDiscovery:
    def __init__(self, api_key: str):
        self.gmaps = googlemaps.Client(key=api_key)
        self.geolocator = Nominatim(user_agent="hyperlocal_lead_generator")

    def _get_coordinates(self, location: str) -> Optional[tuple]:
        """Convert location name/postcode to lat/lng."""
        try:
            # First try with Google Maps Geocoding
            geocode_result = self.gmaps.geocode(location)
            if geocode_result:
                loc = geocode_result[0]['geometry']['location']
                return (loc['lat'], loc['lng'])
        except Exception as e:
            logger.error(f"Error geocoding with Google Maps: {e}")
            
        # Fallback to Nominatim
        try:
            loc = self.geolocator.geocode(location)
            if loc:
                return (loc.latitude, loc.longitude)
        except Exception as e:
            logger.error(f"Error geocoding with Nominatim fallback: {e}")
            
        return None

    @retry(wait=wait_fixed(2), stop=stop_after_attempt(3))
    def search_businesses(self, location: str, radius_km: int, category: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Search for businesses using Google Places API with support for more results via pagination."""
        coords = self._get_coordinates(location)
        if not coords:
            logger.error(f"Could not find coordinates for location: {location}")
            return []

        radius_meters = min(radius_km * 1000, Config.MAX_RADIUS)
        
        logger.info(f"Searching for {category} within {radius_km}km of {location} ({coords})...")
        
        businesses = []
        next_page_token = None
        
        try:
            while len(businesses) < max_results:
                # Nearby Search
                places_result = self.gmaps.places_nearby(
                    location=coords,
                    radius=radius_meters,
                    type=category,
                    page_token=next_page_token
                )
                
                for place in places_result.get('results', []):
                    place_id = place['place_id']
                    try:
                        # Get Place Details
                        details = self.gmaps.place(
                            place_id=place_id,
                            fields=['name', 'formatted_address', 'website', 'address_component', 'place_id', 'geometry']
                        )
                        
                        result = details.get('result', {})
                        city = ""
                        for component in result.get('address_components', []):
                            if 'locality' in component['types']:
                                city = component['long_name']
                                break

                        businesses.append({
                            'business_name': result.get('name', place.get('name')),
                            'category': category,
                            'address': result.get('formatted_address', place.get('vicinity')),
                            'website': result.get('website'),
                            'latitude': result.get('geometry', {}).get('location', {}).get('lat'),
                            'longitude': result.get('geometry', {}).get('location', {}).get('lng'),
                            'place_id': place_id,
                            'city': city
                        })
                        
                        if len(businesses) >= max_results:
                            break
                            
                    except Exception as e:
                        logger.warning(f"Error fetching details for {place_id}: {e}")
                        continue

                next_page_token = places_result.get('next_page_token')
                if not next_page_token:
                    break
                
                # Google requires a short delay before the token becomes valid
                import time
                time.sleep(2)
                
            return businesses

        except Exception as e:
            logger.error(f"Error during Google Places discovery: {e}")
            return businesses
