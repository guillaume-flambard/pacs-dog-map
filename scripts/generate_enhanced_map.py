import pandas as pd
import folium
from folium.plugins import MarkerCluster, GroupedLayerControl
import branca.colormap as cm
import json

def get_marker_color(row):
    """Determine marker color based on priority and status"""
    if row['Status'] == 'Completed':
        return 'green'
    elif row.get('Pregnant?', '').lower() == 'yes':
        return 'red'  # Highest priority
    elif row['Temperament'] == 'Wild':
        return 'orange'  # Medium priority
    elif row['Sex'] == 'Both':
        return 'purple'  # Multiple animals
    else:
        return 'blue'  # Default

def get_marker_icon(row):
    """Get appropriate icon for the marker"""
    if row['Dog/Cat'].lower() == 'cat':
        return 'fa-cat'
    else:
        return 'fa-dog'

def create_popup_html(row):
    """Create enhanced popup HTML with all relevant information"""
    # Handle pregnant status
    pregnant_info = ""
    if row.get('Pregnant?', '').lower() == 'yes':
        pregnant_info = "<b style='color: red;'>🤰 PREGNANT - HIGH PRIORITY</b><br>"
    
    # Handle photos
    photo_html = ""
    if pd.notna(row.get('Photo', '')) and row['Photo'] != '':
        photo_html = f"<br><img src='{row['Photo']}' style='max-width:200px;max-height:150px;'><br>"
    
    # Status badge
    status_color = 'green' if row['Status'] == 'Completed' else 'orange'
    status_html = f"<span style='background-color:{status_color};color:white;padding:2px 6px;border-radius:3px;font-size:11px;'>{row['Status']}</span>"
    
    popup_html = f"""
    <div style='font-family: Arial, sans-serif; max-width: 300px;'>
        {pregnant_info}
        <h4 style='margin:0 0 10px 0; color: #2E86AB;'>{row['Location (Area)']}</h4>
        {status_html}<br><br>
        
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

# Load the CSV file (try multiple sources)
try:
    df = pd.read_csv("data_from_sheets_fixed.csv")  # From coordinate extraction
except FileNotFoundError:
    try:
        df = pd.read_csv("data_from_sheets.csv")  # From Google Sheets sync
    except FileNotFoundError:
        try:
            df = pd.read_csv("PACS_Test_1_List_v2_fixed.csv")
        except FileNotFoundError:
            try:
                df = pd.read_csv("sample_data.csv")
            except FileNotFoundError:
                df = pd.read_csv("PACS_Test_1_List_v2.csv")

# Clean and filter valid coordinates
df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
data = df.dropna(subset=['Latitude', 'Longitude'])

print(f"Processing {len(data)} animals with valid coordinates...")

# Create the enhanced map
map_center = [9.731, 99.990]  # Koh Phangan approx.
m = folium.Map(
    location=map_center, 
    zoom_start=12,
    tiles='OpenStreetMap'
)

# Add different tile layers
folium.TileLayer('OpenStreetMap').add_to(m)
folium.TileLayer('CartoDB positron').add_to(m)

# Create feature groups for filtering
pending_group = folium.FeatureGroup(name="🔴 Pending Animals")
completed_group = folium.FeatureGroup(name="✅ Completed")
pregnant_group = folium.FeatureGroup(name="🤰 Pregnant (HIGH PRIORITY)")
wild_group = folium.FeatureGroup(name="🦁 Wild Animals")
friendly_group = folium.FeatureGroup(name="😊 Friendly Animals")

# Add markers to appropriate groups
for _, row in data.iterrows():
    color = get_marker_color(row)
    icon = get_marker_icon(row)
    popup_html = create_popup_html(row)
    
    marker = folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=folium.Popup(popup_html, max_width=350),
        icon=folium.Icon(
            color=color, 
            icon=icon.replace('fa-', ''), 
            prefix='fa'
        )
    )
    
    # Add to appropriate groups
    if row['Status'] == 'Completed':
        marker.add_to(completed_group)
    else:
        marker.add_to(pending_group)
        
        if row.get('Pregnant?', '').lower() == 'yes':
            marker.add_to(pregnant_group)
        
        if row['Temperament'] == 'Wild':
            marker.add_to(wild_group)
        elif row['Temperament'] == 'Friendly':
            marker.add_to(friendly_group)

# Add all groups to map
pending_group.add_to(m)
completed_group.add_to(m)
pregnant_group.add_to(m)
wild_group.add_to(m)
friendly_group.add_to(m)

# Add layer control
folium.LayerControl().add_to(m)

# Add legend
legend_html = '''
<div style="position: fixed; 
            bottom: 50px; left: 50px; width: 200px; height: 160px; 
            background-color: white; border:2px solid grey; z-index:9999; 
            font-size:14px; padding: 10px">
            
<h4 style="margin-top:0;">🗺️ Map Legend</h4>
<p><i class="fa fa-circle" style="color:red"></i> Pregnant (HIGH PRIORITY)</p>
<p><i class="fa fa-circle" style="color:orange"></i> Wild Animals</p>
<p><i class="fa fa-circle" style="color:purple"></i> Multiple Animals</p>
<p><i class="fa fa-circle" style="color:blue"></i> Standard</p>
<p><i class="fa fa-circle" style="color:green"></i> Completed</p>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Add statistics box
total_animals = len(data)
pending_count = len(data[data['Status'] != 'Completed'])
completed_count = len(data[data['Status'] == 'Completed'])
pregnant_count = len(data[data.get('Pregnant?', '').str.lower() == 'yes'])

stats_html = f'''
<div style="position: fixed; 
            top: 10px; right: 10px; width: 250px; 
            background-color: white; border:2px solid grey; z-index:9999; 
            font-size:14px; padding: 15px; border-radius: 5px;">
            
<h4 style="margin-top:0; color: #2E86AB;">📊 PACS Statistics</h4>
<p><b>Total Animals:</b> {total_animals}</p>
<p><b>Pending:</b> {pending_count}</p>
<p><b>Completed:</b> {completed_count}</p>
<p><b>Pregnant (Priority):</b> {pregnant_count}</p>
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

# Save the enhanced map
m.save("index.html")
print("✅ Enhanced map generated successfully: index.html")
print(f"   - {total_animals} total animals")
print(f"   - {pending_count} pending, {completed_count} completed")
print(f"   - {pregnant_count} pregnant animals (high priority)")