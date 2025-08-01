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
        csv_url = self.config.PUBLISHED_CSV_URL
        
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
             any('type of help' in str(col).lower() for col in df.columns) or  # Or has form-like questions
             'Language' in df.columns and 'Animal' in df.columns)  # Or has key form fields
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
        # Check if column exists first, otherwise skip this filter
        if 'Location (Area)' in df.columns:
            df_clean = df.dropna(subset=['Location (Area)'], how='all')
        else:
            df_clean = df.copy()
        
        # Remove test/invalid data rows - handle NaN values safely
        # Only apply filters if columns exist
        filters = []
        if 'Dog/Cat' in df_clean.columns:
            filters.append(df_clean['Dog/Cat'].fillna('').str.lower().isin(['dog', 'cat']))
        if 'Location (Area)' in df_clean.columns:
            filters.append(df_clean['Location (Area)'].fillna('') != 'Burmese')
            filters.append(df_clean['Location (Area)'].fillna('').str.len() > 2)  # Minimum location name
        if 'Language' in df_clean.columns:
            filters.append(df_clean['Language'].fillna('') != 'Burmese')
        if 'Contact Name' in df_clean.columns:
            filters.append(df_clean['Contact Name'].fillna('').str.len() > 1)  # Minimum contact name
        
        # Apply all valid filters
        if filters:
            combined_filter = filters[0]
            for f in filters[1:]:
                combined_filter = combined_filter & f
            df_clean = df_clean[combined_filter]
        
        # Don't add Priority_Score - not in original sheets
        
        print(f"📊 Data cleaning summary:")
        print(f"   - Total animals: {len(df_clean)}")
        if 'Pregnant?' in df_clean.columns:
            print(f"   - Pregnant animals: {(df_clean['Pregnant?'] == 'Yes').sum()}")
        if 'Location Link' in df_clean.columns:
            print(f"   - Animals with location links: {df_clean['Location Link'].notna().sum()}")
        
        return df_clean
    
    def _map_form_responses_to_standard_format(self, df: pd.DataFrame) -> pd.DataFrame:
        """Map form response columns to standard format using column positions"""
        print("🔄 Converting form responses to standard format...")
        
        # Create new dataframe with standard column names
        standard_df = pd.DataFrame()
        
        # Column mapping by position (robust to name changes)
        # CURRENT STRUCTURE (based on actual data):
        # 0: Timestamp, 1: Language, 2: Procedure, 3: Animal, 4: Sex, 
        # 5: Pregnant, 6: Age, 7: Temperament, 8: Tattoo, 9: Photo, 10: Preview,
        # 11: Google maps link, 12: Location, 13: Extra info, 14: Name, 15: Phone
        
        cols = df.columns.tolist()
        
        # Map each column using position instead of name
        standard_df['Language'] = df.iloc[:, 1].apply(self._fix_language_encoding) if len(cols) > 1 else ''
        
        # Pop-Up Info: Position 2 - Procedure (spay/neuter, medical attention, other)
        standard_df['Pop-Up Info'] = (df.iloc[:, 2] if len(cols) > 2 else pd.Series(dtype='object')).apply(
            lambda x: 'Medical Attention' if 'medical attention' in str(x).lower() else 'Spay/Neuter' if 'spay' in str(x).lower() else str(x) if pd.notna(x) else ''
        )
        
        # Dog/Cat: Position 3 - Animal (dog/cat)
        standard_df['Dog/Cat'] = (df.iloc[:, 3] if len(cols) > 3 else pd.Series(dtype='object')).apply(
            lambda x: 'Dog' if 'dog' in str(x).lower() else 'Cat' if 'cat' in str(x).lower() else str(x) if pd.notna(x) else ''
        )
        
        # Count: Set to 1 for simplified structure (no count field)
        standard_df['No. of Animals'] = '1'
        
        # Sex: Position 4
        standard_df['Sex'] = df.iloc[:, 4] if len(cols) > 4 else ''
        
        # Pregnant: Position 5
        standard_df['Pregnant?'] = df.iloc[:, 5] if len(cols) > 5 else ''
        
        # Age: Position 6
        standard_df['Age'] = df.iloc[:, 6] if len(cols) > 6 else ''
        
        # Temperament: Position 7
        standard_df['Temperament'] = df.iloc[:, 7] if len(cols) > 7 else ''
        
        # Tattoo: Position 8 - New field!
        standard_df['Tattoo'] = df.iloc[:, 8] if len(cols) > 8 else ''
        
        # Photo: Position 9 (main photo)
        standard_df['Photo'] = df.iloc[:, 9] if len(cols) > 9 else ''
        
        # Location fields: Positions 11, 12, 13
        standard_df['Location Link'] = df.iloc[:, 11] if len(cols) > 11 else ''  # Google maps link
        standard_df['Location (Area)'] = df.iloc[:, 12] if len(cols) > 12 else ''  # Location dropdown
        standard_df['Location Details '] = df.iloc[:, 13] if len(cols) > 13 else ''  # Extra info text
        
        # Contact info: Positions 14, 15
        standard_df['Contact Name'] = df.iloc[:, 14] if len(cols) > 14 else ''
        standard_df['Contact Phone #'] = df.iloc[:, 15] if len(cols) > 15 else ''
        
        # Add missing columns
        standard_df['Unshortened Link'] = ''
        standard_df['Latitude'] = ''
        standard_df['Longitude'] = ''
        
        # Photo handling: Use Preview (position 10) if available, otherwise Photo (position 9)
        # Priority: Preview (10) > Photo (9)
        if len(cols) > 10 and df.iloc[:, 10].notna().any():
            standard_df['Photo_Link'] = df.iloc[:, 10]  # Preview
        else:
            standard_df['Photo_Link'] = df.iloc[:, 9] if len(cols) > 9 else ''  # Photo as fallback
        
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
            'pregnant': len(df[df.get('Pregnant?', pd.Series(dtype='object')).fillna('').str.lower() == 'yes']),
            'wild': len(df[df.get('Temperament', '') == 'Wild']),
            'friendly': len(df[df.get('Temperament', '') == 'Friendly'])
        }