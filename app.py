from flask import Flask, render_template, request, redirect, url_for
from sources.utils import update_excel
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
# def map():
#     try :
#         # Load data from the Excel file
#         df = pd.read_excel('earthquake_relief.xlsx')

#         # Create a Folium map centered at an initial location
#         m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=10)

#         # Add markers for each location with counts
#         for index, row in df.iterrows():
#             count = row['Count']
#             location = [row['latitude'], row['longitude']]
            
#             # Create a custom icon for the marker with a red circle and the count inside
#             custom_icon = folium.DivIcon(
#                 icon_size=(30, 30),  # Set the size of the icon
#                 icon_anchor=(15, 15),  # Set the anchor point of the icon
#                 html=f'<div style="background-color: red; color: white; border-radius: 50%; text-align: center; width: 30px; height: 30px; line-height: 30px;">{count}</div>'
#             )
            
#             # Add the marker to the map using the custom icon
#             folium.Marker(
#                 location=location,
#                 icon=custom_icon,
#             ).add_to(m)

#         # Render the map as HTML
#         map_html = m.get_root().render()

#         return render_template('map.html', map_html=map_html)
#     except Exception as e:
#         # Handle exceptions (e.g., file not found, empty DataFrame)
#         return render_template('map.html', message='Error: ' + str(e))


def map():
    try:
        # Load data from the Excel file
        df = pd.read_excel('earthquake_relief.xlsx')

        # Create a Folium map centered at an initial location
        m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=5)

        # Create a MarkerCluster layer
        marker_cluster = MarkerCluster(disable_clustering_at_zoom=5,max_cluster_radius=15).add_to(m)  # Adjust the zoom level as needed

        # Add markers for each location with counts and popup information
        for index, row in df.iterrows():
            count = row['Count']
            location = [row['latitude'], row['longitude']]
            type_of_aid = row['Aid']  # Get Type of Aid from the dataframe
            type_of_vehicle = row['Vehicle']  # Get Type of Vehicle from the dataframe
            count_aid = row['Count'] 

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

            # Create a marker with a popup containing information
            marker = folium.Marker(
                location=location,
                icon=custom_icon,
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
