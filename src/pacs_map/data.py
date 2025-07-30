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
        csv_url = f"https://docs.google.com/spreadsheets/d/{self.config.GOOGLE_SHEET_ID}/export?format=csv&gid={self.config.GOOGLE_SHEET_GID}"
        
        try:
            print("📥 Downloading data from Google Sheets...")
            response = requests.get(csv_url)
            response.raise_for_status()
            
            # Read CSV data
            df = pd.read_csv(StringIO(response.text))
            print(f"✅ Downloaded {len(df)} records")
            
            # Process coordinates
            print("🗺️ Processing coordinates...")
            df, coords_fixed = self.coordinate_extractor.process_dataframe(df)
            print(f"🔧 Fixed coordinates for {coords_fixed} records")
            
            # Clean and process data
            df = self._clean_data(df)
            
            # Save processed data
            data_path = self.config.get_data_path(self.config.SHEETS_DATA_FILE)
            df.to_csv(data_path, index=False)
            print(f"💾 Saved {len(df)} valid records to {data_path}")
            
            return df
            
        except Exception as e:
            print(f"❌ Error syncing from Google Sheets: {e}")
            return None
    
    def load_data(self) -> Optional[pd.DataFrame]:
        """Load data from available sources (in priority order)"""
        data_sources = [
            self.config.get_data_path(self.config.PROCESSED_DATA_FILE),
            self.config.get_data_path(self.config.SHEETS_DATA_FILE),
            "data_from_sheets_fixed.csv",  # Legacy
            "sample_data.csv",  # Legacy
            "PACS_Test_1_List_v2.csv"  # Legacy
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
        
        # Add Status column if missing
        if 'Status' not in df.columns:
            df['Status'] = 'Pending'
        
        # Clean coordinates - replace #REF! and other errors
        df['Latitude'] = df['Latitude'].replace(['#REF!', '#ERROR!', '#N/A'], None)
        df['Longitude'] = df['Longitude'].replace(['#REF!', '#ERROR!', '#N/A'], None)
        df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
        
        # Clean phone numbers - convert to string
        if 'Contact Phone #' in df.columns:
            df['Contact Phone #'] = df['Contact Phone #'].astype(str).replace('nan', '')
        
        # Only keep animals with location info (Area or Link)
        df_clean = df.dropna(subset=['Location (Area)'], how='all')
        
        # Remove test/invalid data rows
        df_clean = df_clean[
            (df_clean['Dog/Cat'].str.lower().isin(['dog', 'cat'])) &
            (df_clean['Location (Area)'] != 'Burmese') &
            (df_clean['Language'] != 'Burmese')
        ]
        
        # Add priority scoring
        df_clean['Priority_Score'] = df_clean.apply(self._calculate_priority, axis=1)
        
        print(f"📊 Data cleaning summary:")
        print(f"   - Total animals: {len(df_clean)}")
        print(f"   - Pregnant animals: {(df_clean['Pregnant?'] == 'Yes').sum()}")
        print(f"   - Animals with location links: {df_clean['Location Link'].notna().sum()}")
        print(f"   - High priority (score > 5): {(df_clean['Priority_Score'] > 5).sum()}")
        
        return df_clean
    
    def _calculate_priority(self, row) -> int:
        """Calculate priority score for an animal"""
        score = 0
        
        if row.get('Pregnant?', '').lower() == 'yes':
            score += self.config.PRIORITY_WEIGHTS['pregnant']
        
        if row.get('Temperament', '').lower() == 'wild':
            score += self.config.PRIORITY_WEIGHTS['wild']
        
        if row.get('Sex', '') == 'Both':
            score += self.config.PRIORITY_WEIGHTS['multiple']
        
        if 'chain' in str(row.get('Location Details ', '')).lower():
            score += self.config.PRIORITY_WEIGHTS['chained']
        
        return score
    
    def get_statistics(self, df: pd.DataFrame) -> dict:
        """Get statistics about the data"""
        valid_coords = df.dropna(subset=['Latitude', 'Longitude'])
        
        return {
            'total_animals': len(df),
            'animals_with_coords': len(valid_coords),
            'pending': len(df[df['Status'] != 'Completed']),
            'completed': len(df[df['Status'] == 'Completed']),
            'pregnant': len(df[df.get('Pregnant?', '').str.lower() == 'yes']),
            'wild': len(df[df.get('Temperament', '') == 'Wild']),
            'friendly': len(df[df.get('Temperament', '') == 'Friendly'])
        }