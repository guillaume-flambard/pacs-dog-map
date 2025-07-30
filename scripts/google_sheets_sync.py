#!/usr/bin/env python3
"""
Google Sheets integration for PACS Dog Map
Sync data directly from Google Sheets to avoid manual CSV exports
"""

import pandas as pd
import requests
import re
from io import StringIO

def extract_coordinates_from_url(url):
    """Extract latitude and longitude from Google Maps URLs"""
    if pd.isna(url) or not url:
        return None, None
    
    # Pattern 1: @lat,lng format (most common)
    match = re.search(r'@(-?\d+\.?\d*),(-?\d+\.?\d*)', url)
    if match:
        return float(match.group(1)), float(match.group(2))
    
    # Pattern 2: 3d coordinates in data parameter
    match = re.search(r'3d(-?\d+\.?\d*)', url)
    if match:
        coords = re.findall(r'3d(-?\d+\.?\d*)', url)
        if len(coords) >= 2:
            return float(coords[0]), float(coords[1])
    
    # Pattern 3: search/lat,lng format
    match = re.search(r'search/(-?\d+\.?\d*),\s*(-?\d+\.?\d*)', url)
    if match:
        return float(match.group(1)), float(match.group(2))
    
    # Pattern 4: place/coordinates with degrees (handling special characters)
    match = re.search(r'place/(\d+)[°Â]+(\d+)\'([\d.]+)[""]+N\+(\d+)[°Â]+(\d+)\'([\d.]+)[""]+E', url)
    if match:
        lat = float(match.group(1)) + float(match.group(2))/60 + float(match.group(3))/3600
        lng = float(match.group(4)) + float(match.group(5))/60 + float(match.group(6))/3600
        return lat, lng
    
    return None, None

def sync_from_google_sheets(sheet_id="1vNW1GtXhWHyVrGJmIEAnlzWQp_QvtfMRD3hzbgYmK9w"):
    """
    Download data directly from Google Sheets
    Make sure the sheet is published to web as CSV
    """
    
    # Google Sheets CSV export URL (using the specific gid from your link)
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=1076834206"
    
    try:
        print("📥 Downloading data from Google Sheets...")
        response = requests.get(csv_url)
        response.raise_for_status()
        
        # Read CSV data
        df = pd.read_csv(StringIO(response.text))
        print(f"✅ Downloaded {len(df)} records")
        
        # Process coordinates
        print("🗺️ Processing coordinates...")
        coords_fixed = 0
        
        for idx, row in df.iterrows():
            if pd.isna(row.get('Latitude')) or pd.isna(row.get('Longitude')):
                # Try Location Link
                if pd.notna(row.get('Location Link')):
                    lat, lng = extract_coordinates_from_url(row['Location Link'])
                    if lat and lng:
                        df.at[idx, 'Latitude'] = lat
                        df.at[idx, 'Longitude'] = lng
                        coords_fixed += 1
                
                # Try Unshortened Link
                elif pd.notna(row.get('Unshortened Link')):
                    lat, lng = extract_coordinates_from_url(row['Unshortened Link'])
                    if lat and lng:
                        df.at[idx, 'Latitude'] = lat
                        df.at[idx, 'Longitude'] = lng
                        coords_fixed += 1
        
        print(f"🔧 Fixed coordinates for {coords_fixed} records")
        
        # Add Status column if missing
        if 'Status' not in df.columns:
            df['Status'] = 'Pending'
        
        # Clean empty rows
        df_clean = df.dropna(subset=['Dog/Cat', 'Location (Area)'], how='all')
        
        # Save locally
        df_clean.to_csv("data_from_sheets.csv", index=False)
        print(f"💾 Saved {len(df_clean)} valid records to data_from_sheets.csv")
        
        return df_clean
        
    except Exception as e:
        print(f"❌ Error syncing from Google Sheets: {e}")
        print("📝 Make sure the Google Sheet is published to web!")
        print("   Go to File > Share > Publish to web > CSV format")
        return None

if __name__ == "__main__":
    # Sync data and generate map
    data = sync_from_google_sheets()
    
    if data is not None:
        print("\n🗺️ Generating updated map...")
        # Import and run the map generator with the new data
        import subprocess
        subprocess.run(["python", "generate_enhanced_map.py"])