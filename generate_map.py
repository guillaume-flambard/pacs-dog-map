import pandas as pd
import folium
from folium.plugins import MarkerCluster

# === 1. Load the CSV file ===
df = pd.read_csv("PACS_Test_1_List_v2.csv")

# Clean and filter valid coordinates
df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
data = df.dropna(subset=['Latitude', 'Longitude'])

# === 2. Create the map ===
map_center = [9.731, 99.990]  # Koh Phangan approx.
m = folium.Map(location=map_center, zoom_start=12)
marker_cluster = MarkerCluster().add_to(m)

# === 3. Add markers ===
for _, row in data.iterrows():
    popup_html = f"""
    <b>Zone:</b> {row['Location (Area)']}<br>
    <b>Animal:</b> {row['Dog/Cat']}<br>
    <b>Sexe:</b> {row['Sex']}<br>
    <b>Age:</b> {row['Age']}<br>
    <b>Contact:</b> {row['Contact Name']}<br>
    <a href="{row['Location Link']}" target="_blank">Voir sur Google Maps</a>
    """
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=folium.Popup(popup_html, max_width=300),
        icon=folium.Icon(color="blue", icon="paw", prefix="fa")
    ).add_to(marker_cluster)

# === 4. Export HTML ===
m.save("index.html")
print("✅ map generated successfully: index.html")