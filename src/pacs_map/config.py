"""
Configuration management for PACS Dog Map
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Main configuration class"""
    
    # Google Sheets
    GOOGLE_SHEET_ID: str = "1PDDu74ZpcZeb6pWxjoRgVtZdHiPb-W2MfBzpT_suUFw"
    GOOGLE_SHEET_GID: str = "1076834206"
    
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