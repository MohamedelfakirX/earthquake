import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

def update_excel(vehicle, aid, location):
    try:
        # Load the existing Excel file or create a new one if it doesn't exist
        df = pd.read_excel('earthquake_relief.xlsx')
        
        new_longitude = location.split(',')[1].strip()
        new_latitude = location.split(',')[0].strip()
        new_point = Point(new_longitude, new_latitude)
        geometry = [Point(lon, lat) for lon, lat in zip(df['longitude'], df['latitude'])]
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')

        buffer_distance_km = 5.0 
        gdf['buffer'] = gdf['geometry'].buffer(buffer_distance_km / 111.32)
        # Check if the new location is within any buffer
        within_buffer = gdf[gdf['buffer'].contains(new_point)]
        print(gdf['buffer'].iloc[0],'\nJJJJJJJJJJJJJJJ :', new_point)
        # Check if the location exists in the DataFrame
        if not within_buffer.empty:
            # Increment the count for each matching location
            gdf.loc[within_buffer.index, 'Count'] += 1

            df = pd.DataFrame(gdf[['Vehicle','Aid','Location','Count', 'latitude','longitude']])
        else:

            # Location doesn't exist; add a new row
            new_row = {'Vehicle': vehicle, 'Aid': aid, 'Location': location, 'Count': 1, 'latitude': new_latitude, 'longitude': new_longitude}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True, axis=0)
        
        # Save the updated DataFrame to the Excel file
        df.to_excel('earthquake_relief.xlsx', index=False)

    except FileNotFoundError:
        # If the file doesn't exist, create a new one
        data = {'Vehicle': [vehicle], 'Aid': [aid], 'Location': [location], 'Count': [1],'latitude':  [location.split(',')[0].strip()], 'longitude':  [location.split(',')[1].strip()]}
        df = pd.DataFrame(data)
        df.to_excel('earthquake_relief.xlsx', index=False)

