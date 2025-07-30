"""
Core map generation functionality for PACS Dog Map
"""

import pandas as pd
import folium
from folium.plugins import MarkerCluster
import os
from datetime import datetime
from typing import Dict, Any

from .config import Config
from .data import DataManager


class PacsMapGenerator:
    """Generate interactive maps for PACS animal tracking"""
    
    def __init__(self, config: Config):
        self.config = config
        self.data_manager = DataManager(config)
        
        # Ensure web directory exists
        os.makedirs(config.WEB_DIR, exist_ok=True)
    
    def generate_map(self, df: pd.DataFrame = None) -> str:
        """Generate the interactive map"""
        # Load data if not provided
        if df is None:
            df = self.data_manager.load_data()
            if df is None:
                raise ValueError("No data available to generate map")
        
        # Filter valid coordinates
        valid_data = df.dropna(subset=['Latitude', 'Longitude'])
        print(f"Processing {len(valid_data)} animals with valid coordinates...")
        
        # Get statistics
        stats = self.data_manager.get_statistics(valid_data)
        
        # Create map
        m = self._create_base_map()
        
        # Add markers
        self._add_markers(m, valid_data)
        
        # Add UI elements
        self._add_legend(m)
        self._add_statistics_panel(m, stats)
        
        # Save map
        output_path = self.config.get_web_path(self.config.OUTPUT_MAP)
        m.save(output_path)
        
        print(f"✅ Enhanced map generated successfully: {output_path}")
        print(f"   - {stats['total_animals']} total animals")
        print(f"   - {stats['pending']} pending, {stats['completed']} completed")
        print(f"   - {stats['pregnant']} pregnant animals (high priority)")
        
        return output_path
    
    def _create_base_map(self) -> folium.Map:
        """Create the base map with tile layers"""
        m = folium.Map(
            location=[self.config.MAP_CENTER_LAT, self.config.MAP_CENTER_LNG],
            zoom_start=self.config.MAP_ZOOM,
            tiles='OpenStreetMap'
        )
        
        # Add additional tile layers
        folium.TileLayer('CartoDB positron').add_to(m)
        
        return m
    
    def _add_markers(self, m: folium.Map, df: pd.DataFrame):
        """Add animal markers to the map"""
        # Create a simple marker cluster for all animals
        from folium.plugins import MarkerCluster
        marker_cluster = MarkerCluster(name="All Animals").add_to(m)
        
        # Add all markers to the cluster
        for _, row in df.iterrows():
            color = self._get_marker_color(row)
            icon = self._get_marker_icon(row)
            popup_html = self._create_popup_html(row)
            
            # Create marker
            marker = folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=folium.Popup(popup_html, max_width=350),
                icon=folium.Icon(
                    color=color,
                    icon=icon.replace('fa-', ''),
                    prefix='fa'
                )
            )
            
            # Add marker to cluster
            marker.add_to(marker_cluster)
    
    def _get_marker_color(self, row: pd.Series) -> str:
        """Determine marker color based on priority and status"""
        if row['Status'] == 'Completed':
            return self.config.MARKER_COLORS['completed']
        elif row.get('Pregnant?', '').lower() == 'yes':
            return self.config.MARKER_COLORS['pregnant']
        elif row.get('Temperament', '') == 'Wild':
            return self.config.MARKER_COLORS['wild']
        elif row.get('Sex', '') == 'Both':
            return self.config.MARKER_COLORS['multiple']
        else:
            return self.config.MARKER_COLORS['default']
    
    def _get_marker_icon(self, row: pd.Series) -> str:
        """Get appropriate icon for the marker"""
        if row.get('Dog/Cat', '').lower() == 'cat':
            return 'fa-cat'
        else:
            return 'fa-dog'
    
    def _create_popup_html(self, row: pd.Series) -> str:
        """Create enhanced popup HTML with all relevant information"""
        # Handle pregnant status
        pregnant_info = ""
        if row.get('Pregnant?', '').lower() == 'yes':
            pregnant_info = "<b style='color: red;'>🤰 PREGNANT - HIGH PRIORITY</b><br>"
        
        # Language info
        language_info = ""
        if pd.notna(row.get('Language', '')) and row['Language'] not in ['', 'English']:
            language_info = f"<b>🌐 Language:</b> {row['Language']}<br>"
        
        # Pop-up info (action needed)
        action_info = ""
        if pd.notna(row.get('Pop-Up Info', '')) and row['Pop-Up Info'] != '':
            action_color = 'red' if 'spay' in row['Pop-Up Info'].lower() else 'blue'
            action_info = f"<span style='background-color:{action_color};color:white;padding:2px 6px;border-radius:3px;font-size:11px;margin-right:5px;'>{row['Pop-Up Info']}</span>"
        
        # Handle photos
        photo_html = ""
        if pd.notna(row.get('Photo', '')) and row['Photo'] != '':
            photo_html = f"<br><img src='{row['Photo']}' style='max-width:200px;max-height:150px;'><br>"
        
        # Status badge
        status = row.get('Status', 'Pending')
        status_color = 'green' if status == 'Completed' else 'orange'
        status_html = f"<span style='background-color:{status_color};color:white;padding:2px 6px;border-radius:3px;font-size:11px;'>{status}</span>"
        
        popup_html = f"""
        <div style='font-family: Arial, sans-serif; max-width: 300px;'>
            {pregnant_info}
            <h4 style='margin:0 0 10px 0; color: #2E86AB;'>{row['Location (Area)']}</h4>
            {action_info}{status_html}<br><br>
            
            {language_info}
            <b>🐾 Animal:</b> {row['Dog/Cat']}<br>
            <b>📊 Count:</b> {row['No. of Animals']}<br>
            <b>⚧ Sex:</b> {row['Sex']}<br>
            <b>🎂 Age:</b> {row['Age']}<br>
            <b>😊 Temperament:</b> {row['Temperament']}<br>
            <b>📞 Contact:</b> {row['Contact Name']} ({row.get('Contact Phone #', 'N/A')})<br>
            
            {photo_html}
            
            <div style='margin-top: 10px;'>
                <a href="{row['Location Link']}" target="_blank" style='background-color:#4285F4;color:white;padding:5px 10px;text-decoration:none;border-radius:3px;font-size:12px;'>📍 View on Google Maps</a>
            </div>
            
            <div style='margin-top: 8px; font-size: 11px; color: #666;'>
                <b>Details:</b> {row.get('Location Details ', 'No additional details')}
            </div>
        </div>
        """
        return popup_html
    
    def _add_legend(self, m: folium.Map):
        """Add legend to the map"""
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 20px; left: 20px; width: 220px; height: auto; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:13px; padding: 12px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    
        <h4 style="margin-top:0; margin-bottom:8px; font-size:14px;">🗺️ Map Legend</h4>
        <div style="margin-bottom:4px;"><i class="fa fa-circle" style="color:red; margin-right:8px;"></i> Pregnant (HIGH PRIORITY)</div>
        <div style="margin-bottom:4px;"><i class="fa fa-circle" style="color:orange; margin-right:8px;"></i> Wild Animals</div>
        <div style="margin-bottom:4px;"><i class="fa fa-circle" style="color:purple; margin-right:8px;"></i> Multiple Animals</div>
        <div style="margin-bottom:4px;"><i class="fa fa-circle" style="color:blue; margin-right:8px;"></i> Standard</div>
        <div style="margin-bottom:0;"><i class="fa fa-circle" style="color:green; margin-right:8px;"></i> Completed</div>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
    
    def _add_statistics_panel(self, m: folium.Map, stats: Dict[str, Any]):
        """Add statistics panel to the map"""
        stats_html = f'''
        <div style="position: fixed; 
                    top: 10px; right: 10px; width: 250px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 15px; border-radius: 5px;">
                    
        <h4 style="margin-top:0; color: #2E86AB;">📊 PACS Statistics</h4>
        <p><b>Total Animals:</b> {stats['total_animals']}</p>
        <p><b>Pending:</b> {stats['pending']}</p>
        <p><b>Completed:</b> {stats['completed']}</p>
        <p><b>Pregnant (Priority):</b> {stats['pregnant']}</p>
        <hr>
        <p style="font-size:12px; color:#666;">
        Last updated: <span id="current-date"></span>
        </p>
        </div>

        <script>
        document.getElementById('current-date').textContent = new Date().toLocaleDateString();
        </script>
        '''
        m.get_root().html.add_child(folium.Element(stats_html))