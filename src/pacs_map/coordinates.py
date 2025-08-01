"""
Coordinate extraction utilities for Google Maps links
"""

import re
import pandas as pd
import requests
from typing import Tuple, Optional


class CoordinateExtractor:
    """Extract coordinates from various Google Maps URL formats"""
    
    def extract_from_url(self, url: str) -> Tuple[Optional[float], Optional[float]]:
        """Extract latitude and longitude from Google Maps URLs"""
        if pd.isna(url) or not url:
            return None, None
        
        # If it's a shortened URL, resolve it first
        if 'maps.app.goo.gl' in url or 'goo.gl' in url:
            try:
                response = requests.head(url, allow_redirects=True, timeout=10)
                url = response.url
            except:
                pass  # Continue with original URL if resolving fails
        
        # Pattern 1: 3d/4d coordinates in data parameter (most precise location)
        coords_3d = re.findall(r'[34]d(-?\d+\.?\d*)', url)
        if len(coords_3d) >= 2:
            return float(coords_3d[0]), float(coords_3d[1])
        
        # Pattern 2: @lat,lng format (fallback, sometimes less precise)
        match = re.search(r'@(-?\d+\.?\d*),(-?\d+\.?\d*)', url)
        if match:
            return float(match.group(1)), float(match.group(2))
        
        # Pattern 3: search/lat,lng format (with optional + and spaces)
        match = re.search(r'search/(-?\d+\.?\d*),\s*\+?(-?\d+\.?\d*)', url)
        if match:
            return float(match.group(1)), float(match.group(2))
        
        # Pattern 4: place/coordinates with degrees (handling special characters)
        match = re.search(r'place/(\d+)[°Â]+(\d+)\'([\d.]+)[""]+N\+(\d+)[°Â]+(\d+)\'([\d.]+)[""]+E', url)
        if match:
            lat = float(match.group(1)) + float(match.group(2))/60 + float(match.group(3))/3600
            lng = float(match.group(4)) + float(match.group(5))/60 + float(match.group(6))/3600
            return lat, lng
        
        return None, None
    
    def process_dataframe(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
        """Process entire dataframe to extract missing coordinates"""
        fixed_count = 0
        
        for idx, row in df.iterrows():
            # Skip if already has coordinates
            if pd.notna(row.get('Latitude')) and pd.notna(row.get('Longitude')):
                continue
            
            # Try Location Link first
            if pd.notna(row.get('Location Link')):
                lat, lng = self.extract_from_url(row['Location Link'])
                if lat and lng:
                    df.at[idx, 'Latitude'] = lat
                    df.at[idx, 'Longitude'] = lng
                    fixed_count += 1
                    continue
            
            # Try Unshortened Link
            if pd.notna(row.get('Unshortened Link')):
                lat, lng = self.extract_from_url(row['Unshortened Link'])
                if lat and lng:
                    df.at[idx, 'Latitude'] = lat
                    df.at[idx, 'Longitude'] = lng
                    fixed_count += 1
                    continue
        
        return df, fixed_count