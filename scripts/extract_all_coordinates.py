#!/usr/bin/env python3
"""
Extract coordinates from all Google Maps links in the PACS data
"""

import pandas as pd
import re

def extract_coordinates_from_url(url):
    """Extract latitude and longitude from Google Maps URLs"""
    if pd.isna(url) or not url:
        return None, None
    
    print(f"Processing URL: {url[:100]}...")
    
    # Pattern 1: @lat,lng format (most common)
    match = re.search(r'@(-?\d+\.?\d*),(-?\d+\.?\d*)', url)
    if match:
        lat, lng = float(match.group(1)), float(match.group(2))
        print(f"  Found @lat,lng: {lat}, {lng}")
        return lat, lng
    
    # Pattern 2: 3d coordinates in data parameter
    match = re.search(r'3d(-?\d+\.?\d*)', url)
    if match:
        coords = re.findall(r'3d(-?\d+\.?\d*)', url)
        if len(coords) >= 2:
            lat, lng = float(coords[0]), float(coords[1])
            print(f"  Found 3d coords: {lat}, {lng}")
            return lat, lng
    
    # Pattern 3: search/lat,lng format (with optional + and spaces)
    match = re.search(r'search/(-?\d+\.?\d*),\s*\+?(-?\d+\.?\d*)', url)
    if match:
        lat, lng = float(match.group(1)), float(match.group(2))
        print(f"  Found search coords: {lat}, {lng}")
        return lat, lng
    
    # Pattern 4: place/coordinates with degrees (handling special characters)
    match = re.search(r'place/(\d+)[°Â]+(\d+)\'([\d.]+)[""]+N\+(\d+)[°Â]+(\d+)\'([\d.]+)[""]+E', url)
    if match:
        lat = float(match.group(1)) + float(match.group(2))/60 + float(match.group(3))/3600
        lng = float(match.group(4)) + float(match.group(5))/60 + float(match.group(6))/3600
        print(f"  Found degree coords: {lat}, {lng}")
        return lat, lng
    
    print("  No coordinates found")
    return None, None

def main():
    # Load data
    df = pd.read_csv("data_from_sheets.csv")
    print(f"Processing {len(df)} records...")
    
    fixed_count = 0
    
    for idx, row in df.iterrows():
        print(f"\n--- Row {idx}: {row.get('Location (Area)', 'Unknown')} ---")
        
        # Skip if already has coordinates
        if pd.notna(row.get('Latitude')) and pd.notna(row.get('Longitude')):
            print(f"  Already has coordinates: {row['Latitude']}, {row['Longitude']}")
            continue
        
        # Try Location Link first
        if pd.notna(row.get('Location Link')):
            lat, lng = extract_coordinates_from_url(row['Location Link'])
            if lat and lng:
                df.at[idx, 'Latitude'] = lat
                df.at[idx, 'Longitude'] = lng
                fixed_count += 1
                print(f"  ✅ Fixed from Location Link")
                continue
        
        # Try Unshortened Link
        if pd.notna(row.get('Unshortened Link')):
            lat, lng = extract_coordinates_from_url(row['Unshortened Link'])
            if lat and lng:
                df.at[idx, 'Latitude'] = lat
                df.at[idx, 'Longitude'] = lng
                fixed_count += 1
                print(f"  ✅ Fixed from Unshortened Link")
                continue
        
        print(f"  ❌ Could not extract coordinates")
    
    print(f"\n🎯 Summary: Fixed {fixed_count} out of {len(df)} records")
    
    # Save updated data
    df.to_csv("data_from_sheets_fixed.csv", index=False)
    print("💾 Saved to data_from_sheets_fixed.csv")
    
    # Count animals with coordinates
    valid_coords = df.dropna(subset=['Latitude', 'Longitude'])
    print(f"📍 Total animals with coordinates: {len(valid_coords)}")
    
    # Generate map
    print("\n🗺️ Generating map with all coordinates...")
    import subprocess
    result = subprocess.run(["python", "generate_enhanced_map.py"], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Map generated successfully!")
    else:
        print("❌ Map generation failed:")
        print(result.stderr)

if __name__ == "__main__":
    main()