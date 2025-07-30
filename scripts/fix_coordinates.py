import pandas as pd
import re
import requests
from urllib.parse import urlparse, parse_qs

def extract_coordinates_from_url(url):
    """Extract latitude and longitude from various Google Maps URL formats"""
    if pd.isna(url) or not url:
        return None, None
    
    # Pattern 1: @lat,lng format
    match = re.search(r'@(-?\d+\.?\d*),(-?\d+\.?\d*)', url)
    if match:
        return float(match.group(1)), float(match.group(2))
    
    # Pattern 2: place/lat%22N+lng%22E format
    match = re.search(r'place/(\d+)°(\d+)\'([\d.]+)\"N\+(\d+)°(\d+)\'([\d.]+)\"E', url)
    if match:
        lat = float(match.group(1)) + float(match.group(2))/60 + float(match.group(3))/3600
        lng = float(match.group(4)) + float(match.group(5))/60 + float(match.group(6))/3600
        return lat, lng
    
    # Pattern 3: /data= with 3d coordinates
    match = re.search(r'3d(-?\d+\.?\d*)', url)
    if match:
        coords = re.findall(r'3d(-?\d+\.?\d*)', url)
        if len(coords) >= 2:
            return float(coords[0]), float(coords[1])
    
    return None, None

# Load the CSV
df = pd.read_csv("PACS_Test_1_List_v2.csv")

# Fix coordinates for all rows
print("Fixing coordinates...")
for idx, row in df.iterrows():
    if pd.isna(row['Latitude']) or pd.isna(row['Longitude']) or row['Latitude'] == '#REF!' or row['Longitude'] == '#REF!':
        # Try to extract from Location Link
        if pd.notna(row['Location Link']):
            lat, lng = extract_coordinates_from_url(row['Location Link'])
            if lat and lng:
                df.at[idx, 'Latitude'] = lat
                df.at[idx, 'Longitude'] = lng
                print(f"Fixed coordinates for row {idx}: {lat}, {lng}")
        
        # Try to extract from Unshortened Link
        elif pd.notna(row['Unshortened Link']):
            lat, lng = extract_coordinates_from_url(row['Unshortened Link'])
            if lat and lng:
                df.at[idx, 'Latitude'] = lat
                df.at[idx, 'Longitude'] = lng
                print(f"Fixed coordinates for row {idx} from unshortened: {lat}, {lng}")

# Clean up empty rows
df_clean = df.dropna(subset=['Dog/Cat', 'Location (Area)'], how='all')

# Add status column for tracking completion
if 'Status' not in df_clean.columns:
    df_clean['Status'] = 'Pending'

# Save the cleaned CSV
df_clean.to_csv("PACS_Test_1_List_v2_fixed.csv", index=False)
print(f"✅ Fixed CSV saved with {len(df_clean)} valid records")