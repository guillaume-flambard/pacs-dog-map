"""
Batch operations for PACS Dog Map
"""

import pandas as pd
from typing import List, Optional
from .config import Config
from .data import DataManager


class BatchOperations:
    """Handle batch operations on animal data"""
    
    def __init__(self, config: Config):
        self.config = config
        self.data_manager = DataManager(config)
    
    def mark_completed(self, animal_ids: List[int]) -> int:
        """Mark specific animals as completed"""
        df = self.data_manager.load_data()
        if df is None:
            print("❌ No data found!")
            return 0
        
        updated_count = 0
        for idx in animal_ids:
            if idx < len(df):
                df.at[idx, 'Status'] = 'Completed'
                location = df.at[idx, 'Location (Area)']
                animal = df.at[idx, 'Dog/Cat']
                print(f"✅ Marked {animal} at {location} as completed")
                updated_count += 1
        
        # Save updated data
        if updated_count > 0:
            self.data_manager.save_processed_data(df)
            print(f"💾 Updated {updated_count} records")
        
        return updated_count
    
    def list_pending(self) -> Optional[pd.DataFrame]:
        """List all pending animals"""
        df = self.data_manager.load_data()
        if df is None:
            return None
        
        pending = df[df['Status'] != 'Completed']
        print(f"\n📋 {len(pending)} PENDING ANIMALS:\n")
        
        for idx, row in pending.iterrows():
            priority = "🚨 HIGH PRIORITY" if row.get('Pregnant?', '').lower() == 'yes' else ""
            print(f"ID {idx}: {row['Dog/Cat']} at {row['Location (Area)']} - {row['Temperament']} {priority}")
            print(f"    Contact: {row['Contact Name']} ({row.get('Contact Phone #', 'N/A')})")
            print(f"    Status: {row['Status']}\n")
        
        return pending
    
    def generate_priority_list(self) -> Optional[pd.DataFrame]:
        """Generate priority-sorted list for field work"""
        df = self.data_manager.load_data()
        if df is None:
            return None
        
        # Get pending animals sorted by priority
        pending = df[df['Status'] != 'Completed']
        priority_list = pending.sort_values('Priority_Score', ascending=False)
        
        print("🎯 PRIORITY ORDER FOR FIELD WORK:\n")
        for idx, row in priority_list.iterrows():
            score_text = f"Priority: {row['Priority_Score']}"
            print(f"ID {idx}: {row['Location (Area)']} - {row['Dog/Cat']} ({row['Sex']}) - {score_text}")
            
            if row.get('Pregnant?', '').lower() == 'yes':
                print("    🚨 PREGNANT - URGENT!")
            if row.get('Temperament', '') == 'Wild':
                print("    🦁 WILD - Difficult to catch")
            if 'chain' in str(row.get('Location Details ', '')).lower():
                print("    ⛓️ CHAINED - Needs owner permission")
                
            print(f"    Maps: {row['Location Link']}\n")
        
        return priority_list
    
    def get_animals_by_location(self, location: str) -> Optional[pd.DataFrame]:
        """Get all animals in a specific location"""
        df = self.data_manager.load_data()
        if df is None:
            return None
        
        location_animals = df[df['Location (Area)'].str.contains(location, case=False, na=False)]
        
        if len(location_animals) == 0:
            print(f"No animals found in location containing '{location}'")
            return None
        
        print(f"\n🗺️ ANIMALS IN {location.upper()}:\n")
        for idx, row in location_animals.iterrows():
            status_icon = "✅" if row['Status'] == 'Completed' else "⏳"
            print(f"{status_icon} ID {idx}: {row['Dog/Cat']} - {row['Temperament']} - {row['Status']}")
            print(f"    Contact: {row['Contact Name']}")
            print(f"    Details: {row.get('Location Details ', 'N/A')}\n")
        
        return location_animals
    
    def export_field_report(self, output_path: str = None) -> str:
        """Export a field work report"""
        df = self.data_manager.load_data()
        if df is None:
            raise ValueError("No data available")
        
        if output_path is None:
            output_path = self.config.get_data_path("field_report.csv")
        
        # Create field report with relevant columns
        field_columns = [
            'Location (Area)', 'Dog/Cat', 'No. of Animals', 'Sex', 'Age', 
            'Temperament', 'Pregnant?', 'Status', 'Priority_Score',
            'Contact Name', 'Contact Phone #', 'Location Details ',
            'Location Link'
        ]
        
        # Filter and sort by priority
        pending = df[df['Status'] != 'Completed']
        field_report = pending[field_columns].sort_values('Priority_Score', ascending=False)
        
        field_report.to_csv(output_path, index=True)
        print(f"📋 Field report exported to {output_path}")
        print(f"   - {len(field_report)} animals pending sterilization")
        
        return output_path