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
        
        # Check if this is form responses data by structure (timestamp + many columns)
        is_form_data = (
            len(df.columns) > 10 and  # Form has many columns
            ('Horodateur' in df.columns or 'Timestamp' in df.columns or  # Has timestamp
             any('type of help' in str(col).lower() for col in df.columns))  # Or has form-like questions
        )
        
        if is_form_data:
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
        """Map form response columns to standard format using column positions"""
        print("🔄 Converting form responses to standard format...")
        
        # Create new dataframe with standard column names
        standard_df = pd.DataFrame()
        
        # Column mapping by position (robust to name changes)
        # Position mapping based on Google Form structure:
        # 0: Timestamp, 1: Language, 2: Help type, 3: Animal type, 4: Count, 
        # 5: Gender, 6: Pregnant, 7: Age, 8: Temperament, 9: Area, 
        # 10: Details, 11: Maps Link, 12: Name, 13: Phone, 14: Upload photo, 15: Your photo, 16: Preview
        
        cols = df.columns.tolist()
        
        # Map each column using position instead of name
        standard_df['Language'] = df.iloc[:, 1].apply(self._fix_language_encoding) if len(cols) > 1 else ''
        
        # Pop-Up Info: Position 2 - Help type
        standard_df['Pop-Up Info'] = (df.iloc[:, 2] if len(cols) > 2 else pd.Series(dtype='object')).apply(
            lambda x: 'Ask for Info' if 'Medical attention' in str(x) else 'Spay/Neuter' if 'Spay/Neuter' in str(x) else str(x) if pd.notna(x) else ''
        )
        
        # Dog/Cat: Position 3 - Animal type
        standard_df['Dog/Cat'] = (df.iloc[:, 3] if len(cols) > 3 else pd.Series(dtype='object')).apply(
            lambda x: 'Dog' if 'Dog' in str(x) else 'Cat' if 'Cat' in str(x) else str(x) if pd.notna(x) else ''
        )
        
        # Count: Position 4
        standard_df['No. of Animals'] = df.iloc[:, 4] if len(cols) > 4 else ''
        
        # Sex: Position 5 - Gender
        standard_df['Sex'] = (df.iloc[:, 5] if len(cols) > 5 else pd.Series(dtype='object')).apply(
            lambda x: 'Both' if 'Both' in str(x) or 'mixed' in str(x) else 'Male' if 'Male only' in str(x) else 'Female' if 'Female only' in str(x) else str(x) if pd.notna(x) else ''
        )
        
        # Pregnant: Position 6
        standard_df['Pregnant?'] = (df.iloc[:, 6] if len(cols) > 6 else pd.Series(dtype='object')).apply(
            lambda x: 'Yes' if 'Yes' in str(x) else 'No'
        )
        
        # Age: Position 7
        standard_df['Age'] = (df.iloc[:, 7] if len(cols) > 7 else pd.Series(dtype='object')).apply(
            lambda x: 'Puppy (>6mnth)' if 'puppies' in str(x) or 'kittens' in str(x) or 'under 6' in str(x) 
                     else 'Teenager (6mnth - 1yr)' if 'Teenagers' in str(x) or '6 months to 1 year' in str(x)
                     else 'Adult' if 'Adult' in str(x) 
                     else str(x) if pd.notna(x) else ''
        )
        
        # Temperament: Position 8
        standard_df['Temperament'] = (df.iloc[:, 8] if len(cols) > 8 else pd.Series(dtype='object')).apply(
            lambda x: 'Friendly' if 'Friendly' in str(x) or 'approaches people' in str(x)
                     else 'Wild' if any(word in str(x) for word in ['Wild', 'Scared', 'runs away', 'Mixed', 'behavior'])
                     else str(x) if pd.notna(x) else ''
        )
        
        # Location fields: Positions 9, 10, 11
        standard_df['Location (Area)'] = df.iloc[:, 9] if len(cols) > 9 else ''
        standard_df['Location Details '] = df.iloc[:, 10] if len(cols) > 10 else ''  # Note trailing space
        standard_df['Location Link'] = df.iloc[:, 11] if len(cols) > 11 else ''
        
        # Contact info: Positions 12, 13
        standard_df['Contact Name'] = df.iloc[:, 12] if len(cols) > 12 else ''
        standard_df['Contact Phone #'] = df.iloc[:, 13] if len(cols) > 13 else ''
        
        # Handle photos by position: 14=Upload, 15=Your photo, 16=Preview
        # Prioritize Cloudinary preview (16) > Your photo (15) > Upload (14)
        if len(cols) > 16 and pd.notna(df.iloc[:, 16]).any():
            standard_df['Photo'] = df.iloc[:, 16]  # Preview (Cloudinary)
        elif len(cols) > 15 and pd.notna(df.iloc[:, 15]).any():
            standard_df['Photo'] = df.iloc[:, 15]  # Your photo (Cloudinary)
        elif len(cols) > 14:
            standard_df['Photo'] = df.iloc[:, 14]  # Upload photos (Google Drive)
        else:
            standard_df['Photo'] = ''
        
        # Add missing columns
        standard_df['Unshortened Link'] = ''
        standard_df['Latitude'] = ''
        standard_df['Longitude'] = ''
        
        # Add full resolution photo link (use 'Your photo' position 15 as full resolution)
        if len(cols) > 15:
            standard_df['Photo_Link'] = df.iloc[:, 15]  # Your photo (Cloudinary full res)
        elif len(cols) > 16:
            standard_df['Photo_Link'] = df.iloc[:, 16]  # Preview as fallback
        else:
            standard_df['Photo_Link'] = ''
        
        print(f"✅ Converted {len(standard_df)} form responses to standard format")
        return standard_df
    
    def _fix_language_encoding(self, language_text) -> str:
        """Fix encoding issues with Thai and other non-Latin languages"""
        if pd.isna(language_text) or not language_text:
            return ""
        
        # Common language mappings to fix encoding issues
        language_mappings = {
            'Thai': 'Thai (ไทย)',
            'ภาษาไทย': 'Thai (ไทย)', 
            'à¸ à¸²à¸©à¸²à¹à¸à¸¢': 'Thai (ไทย)',
            'Burmese': 'Burmese (မြန်မာ)',
            'မြန်မာဘာသာ': 'Burmese (မြန်မာ)',
            'English': 'English'
        }
        
        text = str(language_text).strip()
        
        # Check direct mapping first
        if text in language_mappings:
            return language_mappings[text]
        
        # Try to detect mangled Thai characters
        if any(char in text for char in ['à¸', 'à¹', 'à¸©', 'à¸²']):
            return 'Thai (ไทย)'
        
        # Try to detect mangled Burmese characters  
        if any(char in text for char in ['á€', 'á€™', 'á€¼', 'á€­']):
            return 'Burmese (မြန်မာ)'
        
        return text
    
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