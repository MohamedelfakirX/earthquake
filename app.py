from flask import Flask, render_template, request, redirect, url_for
from sources.utils import update_excel, merge_by_distance_coords
import folium
import pandas as pd
from folium.plugins import MarkerCluster  # Import MarkerCluster

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    vehicle = request.form['vehicle']
    aid = request.form['aid']
    location = request.form['location']

    # Process and store this data in the Excel file
    update_excel(vehicle, aid, location)

    return redirect(url_for('index'))

@app.route('/map')

def map():
    try:
        # Load data from the Excel file
        df = pd.read_excel('earthquake_relief.xlsx')
        df_location = pd.read_excel('locations.xlsx')

        df_merged = merge_by_distance_coords(df,df_location,5)
        df_merged.to_excel('temp_csv.xlsx')
        # Create a Folium map centered at an initial location
        m = folium.Map(location=[df_merged['latitude'].quantile(0.7), df_merged['longitude'].quantile(0.7)], zoom_start=5)

        # Create a MarkerCluster layer
        marker_cluster = MarkerCluster(disable_clustering_at_zoom=5,max_cluster_radius=15).add_to(m)  # Adjust the zoom level as needed

        # Add markers for each location with counts and popup information
        for index, row in df_merged.iterrows():
            
            location = [row['latitude'], row['longitude']]
            try :
                count = row['Count']
                type_of_aid = row['Aid']  # Get Type of Aid from the dataframe
                type_of_vehicle = row['Vehicle']  # Get Type of Vehicle from the dataframe
                count_aid = row['Count'] 
            except :
                count = None
                type_of_aid = None  # Get Type of Aid from the dataframe
                type_of_vehicle = None  # Get Type of Vehicle from the dataframe
                count_aid = None
            # Create a custom icon for the marker with the count inside
            custom_icon = folium.DivIcon(
                icon_size=(30, 30),
                icon_anchor=(15, 15),
                html=f'<div style="background-color: red; color: white; border-radius: 50%; text-align: center; width: 30px; height: 30px; line-height: 30px;">{count}</div>'
            )
            # Create a custom popup with dynamic size and Arabic text alignment
            popup_content = f'''
                <div style="
                    width: auto;
                    max-width: 300px;  /* Set a maximum width for the popup */
                    text-align: right;  /* right-to-left text direction */
                ">
                    <div style="font-weight: bold;">نوع المساعدة : {type_of_aid}</div>
                    <div style="font-weight: bold;">نوع المركبة : {type_of_vehicle}</div>
                    <div style="font-weight: bold;">{count_aid} : عدد المساعدات</div>
                </div>
            '''
            location_icon = folium.Icon(color='red', icon='home', prefix='fa')

            # Create a marker with a popup containing information
            marker = folium.Marker(
                location=location,
                icon=location_icon, # custom_icon
                popup=folium.Popup(popup_content, max_width=300)  # Popup information
            )

            marker.add_to(marker_cluster)  # Add the marker to the MarkerCluster layer

        # Render the map as HTML
        map_html = m.get_root().render()

        return render_template('map.html', map_html=map_html)
    except Exception as e:
        return str(e)



if __name__ == '__main__':
    app.run(debug=True)
