"""
Configuration management for PACS Dog Map
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class Config:
    """Main configuration class"""
    
    # Google Sheets - Form Responses Spreadsheet
    # THESE ARE EXAMPLE VALUES - PUT YOUR REAL IDs IN .env FILE
    # To find these IDs:
    # 1. GOOGLE_SHEET_ID: From your sheet URL after /spreadsheets/d/
    # 2. GOOGLE_SHEET_GID: From your sheet URL after #gid= or from export URL
    # 3. GOOGLE_SHEET_PUBLISHED_ID: From File -> Share -> Publish to web -> CSV link
    GOOGLE_SHEET_ID: str = "1EXAMPLE_SHEET_ID"
    GOOGLE_SHEET_GID: str = "0"  # Example GID
    GOOGLE_SHEET_PUBLISHED_ID: str = "2PACX-EXAMPLE_PUBLISHED_ID"
    
    # Published CSV URL (automatically generated from sheet IDs above)
    @property
    def PUBLISHED_CSV_URL(self) -> str:
        return f"https://docs.google.com/spreadsheets/d/e/{self.GOOGLE_SHEET_PUBLISHED_ID}/pub?gid={self.GOOGLE_SHEET_GID}&single=true&output=csv"
    
    # Cloudinary Configuration
    # THESE ARE EXAMPLE VALUES - PUT YOUR REAL VALUES IN .env FILE
    CLOUDINARY_CLOUD_NAME: str = "your-cloud-name"
    CLOUDINARY_UPLOAD_PRESET: str = "your-preset"
    
    # Map settings
    MAP_CENTER_LAT: float = 9.731
    MAP_CENTER_LNG: float = 99.990
    MAP_ZOOM: int = 12
    
    # File paths
    DATA_DIR: str = "data"
    WEB_DIR: str = "web"
    OUTPUT_MAP: str = "index.html"
    
    # Data files
    SHEETS_DATA_FILE: str = "data_from_sheets.csv"
    PROCESSED_DATA_FILE: str = "processed_data.csv"
    BACKUP_DATA_FILE: str = "backup_data.csv"
    
    # Map styling
    MARKER_COLORS = {
        'completed': 'green',
        'pregnant': 'red',
        'wild': 'orange', 
        'multiple': 'purple',
        'default': 'blue'
    }
    
    # Priority scoring
    PRIORITY_WEIGHTS = {
        'pregnant': 10,
        'wild': 5,
        'multiple': 3,
        'chained': 2
    }
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment variables"""
        return cls(
            GOOGLE_SHEET_ID=os.getenv('GOOGLE_SHEET_ID', cls.GOOGLE_SHEET_ID),
            GOOGLE_SHEET_GID=os.getenv('GOOGLE_SHEET_GID', cls.GOOGLE_SHEET_GID),
            GOOGLE_SHEET_PUBLISHED_ID=os.getenv('GOOGLE_SHEET_PUBLISHED_ID', cls.GOOGLE_SHEET_PUBLISHED_ID),
            CLOUDINARY_CLOUD_NAME=os.getenv('CLOUDINARY_CLOUD_NAME', cls.CLOUDINARY_CLOUD_NAME),
            CLOUDINARY_UPLOAD_PRESET=os.getenv('CLOUDINARY_UPLOAD_PRESET', cls.CLOUDINARY_UPLOAD_PRESET),
            MAP_CENTER_LAT=float(os.getenv('MAP_CENTER_LAT', cls.MAP_CENTER_LAT)),
            MAP_CENTER_LNG=float(os.getenv('MAP_CENTER_LNG', cls.MAP_CENTER_LNG)),
            MAP_ZOOM=int(os.getenv('MAP_ZOOM', cls.MAP_ZOOM)),
        )
    
    def get_data_path(self, filename: str) -> str:
        """Get full path for data file"""
        return os.path.join(self.DATA_DIR, filename)
    
    def get_web_path(self, filename: str) -> str:
        """Get full path for web file"""  
        return os.path.join(self.WEB_DIR, filename)
    
    def get_cloudinary_config_js(self) -> str:
        """Get JavaScript configuration for Cloudinary widget"""
        return f"""{{
      cloudName: '{self.CLOUDINARY_CLOUD_NAME}',
      uploadPreset: '{self.CLOUDINARY_UPLOAD_PRESET}'
    }}"""
    
