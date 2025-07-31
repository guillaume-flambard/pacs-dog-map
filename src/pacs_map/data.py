"""
Data management for PACS Dog Map
"""

import pandas as pd
import requests
from io import StringIO
from typing import Optional
import os
from datetime import datetime

from .config import Config
from .coordinates import CoordinateExtractor


class DataManager:
    """Handle data loading, processing, and saving"""
    
    def __init__(self, config: Config):
        self.config = config
        self.coordinate_extractor = CoordinateExtractor()
        
        # Ensure data directory exists
        os.makedirs(config.DATA_DIR, exist_ok=True)
    
    def sync_from_google_sheets(self) -> Optional[pd.DataFrame]:
        """Download and process data from Google Sheets"""
        # Use published CSV URL for form responses spreadsheet (more reliable for GitHub Actions)
        csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQLJp4fulYq6Y8pnvjOGllpGYA_I3ZMNeO-eHgAB94hl2TIPA_CmSzVafXcYklYidLWvLF2N9dObwYE/pub?gid=1857135137&single=true&output=csv"
        
        # Fallback to old method if published URL fails
        fallback_url = f"https://docs.google.com/spreadsheets/d/{self.config.GOOGLE_SHEET_ID}/export?format=csv&gid={self.config.GOOGLE_SHEET_GID}"
        
        # Try published URL first, then fallback
        for url_desc, url in [("published", csv_url), ("direct export", fallback_url)]:
            try:
                print(f"📥 Downloading data from Google Sheets ({url_desc})...")
                response = requests.get(url)
                response.raise_for_status()
                
                # Check if we got HTML (redirect) instead of CSV
                if response.text.startswith('<HTML>') or response.text.startswith('<!DOCTYPE'):
                    print(f"⚠️ Got HTML redirect from {url_desc} URL, trying next method...")
                    continue
                
                # Read CSV data
                df = pd.read_csv(StringIO(response.text))
                print(f"✅ Downloaded {len(df)} records from {url_desc} URL")
                break
                
            except Exception as e:
                print(f"❌ Failed to download from {url_desc} URL: {e}")
                if url_desc == "direct export":  # Last attempt failed
                    raise e
                continue
        
        # Clean and process data first (includes form mapping)
        df = self._clean_data(df)
        
        # Then process coordinates on the cleaned/mapped data
        print("🗺️ Processing coordinates...")
        df, coords_fixed = self.coordinate_extractor.process_dataframe(df)
        print(f"🔧 Fixed coordinates for {coords_fixed} records")
        
        # Save processed data
        data_path = self.config.get_data_path(self.config.SHEETS_DATA_FILE)
        df.to_csv(data_path, index=False)
        print(f"💾 Saved {len(df)} valid records to {data_path}")
        
        return df
    
    def load_data(self) -> Optional[pd.DataFrame]:
        """Load data from available sources (in priority order)"""
        data_sources = [
            # Priority 1: Fresh sync from Google Sheets
            self.config.get_data_path(self.config.SHEETS_DATA_FILE),
            # Priority 2: Previously processed data (fallback)
            self.config.get_data_path(self.config.PROCESSED_DATA_FILE),
            # Legacy files for compatibility
            "data_from_sheets_fixed.csv",
            "sample_data.csv", 
            "PACS_Test_1_List_v2.csv"
        ]
        
        for source in data_sources:
            try:
                df = pd.read_csv(source)
                print(f"📂 Loaded data from {source}")
                return self._clean_data(df)
            except FileNotFoundError:
                continue
        
        print("❌ No data sources found!")
        return None
    
    def save_processed_data(self, df: pd.DataFrame) -> str:
        """Save processed data with timestamp"""
        output_path = self.config.get_data_path(self.config.PROCESSED_DATA_FILE)
        df.to_csv(output_path, index=False)
        
        # Also create backup with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.config.get_data_path(f"backup_{timestamp}.csv")
        df.to_csv(backup_path, index=False)
        
        return output_path
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize data"""
        # Create a copy to avoid warnings
        df = df.copy()
        
        # Check if this is form responses data and map columns
        if 'Horodateur' in df.columns or 'What type of help does this animal need?' in df.columns:
            df = self._map_form_responses_to_standard_format(df)
        
        # Clean coordinates and other problematic values
        for col in df.columns:
            if col in df.columns:  # Check if column exists after mapping
                df[col] = df[col].replace(['#REF!', '#ERROR!', '#N/A', '#NAME?'], '')
        
        # Add coordinate columns if they don't exist
        if 'Latitude' not in df.columns:
            df['Latitude'] = ''
        if 'Longitude' not in df.columns:
            df['Longitude'] = ''
            
        df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
        
        # Clean phone numbers - convert to string
        if 'Contact Phone #' in df.columns:
            df['Contact Phone #'] = df['Contact Phone #'].astype(str).replace('nan', '')
        
        # Only keep animals with location info (Area or Link)
        df_clean = df.dropna(subset=['Location (Area)'], how='all')
        
        # Remove test/invalid data rows - handle NaN values safely
        df_clean = df_clean[
            (df_clean['Dog/Cat'].fillna('').str.lower().isin(['dog', 'cat'])) &
            (df_clean['Location (Area)'].fillna('') != 'Burmese') &
            (df_clean['Language'].fillna('') != 'Burmese') &
            (df_clean['Location (Area)'].fillna('').str.len() > 2) &  # Minimum location name
            (df_clean['Contact Name'].fillna('').str.len() > 1)       # Minimum contact name
        ]
        
        # Don't add Priority_Score - not in original sheets
        
        print(f"📊 Data cleaning summary:")
        print(f"   - Total animals: {len(df_clean)}")
        print(f"   - Pregnant animals: {(df_clean['Pregnant?'] == 'Yes').sum()}")
        print(f"   - Animals with location links: {df_clean['Location Link'].notna().sum()}")
        
        return df_clean
    
    def _map_form_responses_to_standard_format(self, df: pd.DataFrame) -> pd.DataFrame:
        """Map form response columns to standard format"""
        print("🔄 Converting form responses to standard format...")
        
        # Create new dataframe with standard column names
        standard_df = pd.DataFrame()
        
        # Map each column from form format to standard format
        standard_df['Language'] = df.get('Language', '')
        
        # Pop-Up Info: "Medical attention / Ask for information" -> "Ask for Info"
        standard_df['Pop-Up Info'] = df.get('What type of help does this animal need?', '').apply(
            lambda x: 'Ask for Info' if 'Medical attention' in str(x) else 'Spay/Neuter' if 'Spay/Neuter' in str(x) else str(x) if pd.notna(x) else ''
        )
        
        # Dog/Cat: "Dog 🐕" -> "Dog"
        standard_df['Dog/Cat'] = df.get('What type of animal is this?', '').apply(
            lambda x: 'Dog' if 'Dog' in str(x) else 'Cat' if 'Cat' in str(x) else str(x) if pd.notna(x) else ''
        )
        
        standard_df['No. of Animals'] = df.get('How many animals are at this location?', '')
        
        # Sex: "Both male and female (mixed group)" -> "Both"
        standard_df['Sex'] = df.get('What is the gender of the animal(s)?', '').apply(
            lambda x: 'Both' if 'Both' in str(x) or 'mixed' in str(x) else 'Male' if 'Male only' in str(x) else 'Female' if 'Female only' in str(x) else str(x) if pd.notna(x) else ''
        )
        
        # Pregnant: "No - Not pregnant" -> "No"
        standard_df['Pregnant?'] = df.get('Are any of the animals pregnant?', '').apply(
            lambda x: 'Yes' if 'Yes' in str(x) else 'No'
        )
        
        # Age: "Young puppies/kittens (under 6 months)" -> "Puppy (>6mnth)"
        standard_df['Age'] = df.get('How old do the animals appear to be?', '').apply(
            lambda x: 'Puppy (>6mnth)' if 'puppies' in str(x) or 'kittens' in str(x) or 'under 6' in str(x) 
                     else 'Teenager (6mnth - 1yr)' if 'Teenagers' in str(x) or '6 months to 1 year' in str(x)
                     else 'Adult' if 'Adult' in str(x) 
                     else str(x) if pd.notna(x) else ''
        )
        
        # Temperament: "Mixed behavior" -> "Wild"
        standard_df['Temperament'] = df.get('How do the animals behave around people?', '').apply(
            lambda x: 'Friendly' if 'Friendly' in str(x) or 'approaches people' in str(x)
                     else 'Wild' if any(word in str(x) for word in ['Wild', 'Scared', 'runs away', 'Mixed', 'behavior'])
                     else str(x) if pd.notna(x) else ''
        )
        
        standard_df['Location (Area)'] = df.get('Where did you see these animals?', '')
        standard_df['Location Link'] = df.get('Share the Google Maps location', '')
        standard_df['Location Details '] = df.get('Describe the exact location', '')  # Note trailing space
        standard_df['Contact Name'] = df.get('Your name', '')
        standard_df['Contact Phone #'] = df.get('Your phone number', '')
        standard_df['Photo'] = df.get('Upload photos of the animal(s)', '')
        
        # Add missing columns
        standard_df['Unshortened Link'] = ''
        standard_df['Latitude'] = ''
        standard_df['Longitude'] = ''
        
        print(f"✅ Converted {len(standard_df)} form responses to standard format")
        return standard_df
    
    def get_statistics(self, df: pd.DataFrame) -> dict:
        """Get statistics about the data"""
        valid_coords = df.dropna(subset=['Latitude', 'Longitude'])
        
        return {
            'total_animals': len(df),
            'animals_with_coords': len(valid_coords),
            'pregnant': len(df[df.get('Pregnant?', '').str.lower() == 'yes']),
            'wild': len(df[df.get('Temperament', '') == 'Wild']),
            'friendly': len(df[df.get('Temperament', '') == 'Friendly'])
        }