from geopy.geocoders import Nominatim
import pandas as pd
import time

# Initialize geolocator
geolocator = Nominatim(user_agent="arabic_osint_dashboard")

# Function to extract and geocode locations
def extract_and_geocode(df, location_column='title_en'):
    locations = []
    for headline in df[location_column]:
        try:
            # Geocode headline (looking for place names)
            location = geolocator.geocode(headline, timeout=10)
            if location:
                locations.append({
                    'headline': headline,
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                    'location_name': location.address
                })
            else:
                locations.append({
                    'headline': headline,
                    'latitude': None,
                    'longitude': None,
                    'location_name': None
                })
        except Exception as e:
            print(f"Error geocoding: {headline} - {e}")
            locations.append({
                'headline': headline,
                'latitude': None,
                'longitude': None,
                'location_name': None
            })
        # Pause to avoid API rate limits
        time.sleep(1)

    return pd.DataFrame(locations)
