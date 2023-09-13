import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from shapely.ops import nearest_points
from geopy.distance import geodesic
from shapely import wkt 
from scipy.spatial.distance import cdist
from haversine import haversine

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
        # print(gdf['buffer'].iloc[0],'\nJJJJJJJJJJJJJJJ :', new_point)
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
        data = {'Vehicle': [vehicle], 'Aid': [aid], 'location': [location], 'Count': [1],'latitude':  [location.split(',')[0].strip()], 'longitude':  [location.split(',')[1].strip()]}
        df = pd.DataFrame(data)
        df.to_excel('earthquake_relief.xlsx', index=False)


def merge_by_distance_coords(df1,df_location,distance_threshold_km):
# Convert the DataFrame to Shapely Point geometries
    df1['geometry'] = [Point(lon, lat) for lon, lat in zip(df1['longitude'], df1['latitude'])]
    df_location['geometry'] = [Point(lon, lat) for lon, lat in zip(df_location['longitude'], df_location['latitude'])]

    merged_data = []

    for index1, row1 in df1.iterrows():
        for index2, row2 in df_location.iterrows():
            # Calculate the distance between the two points
            distance = geodesic((row1['latitude'], row1['longitude']), (row2['latitude'], row2['longitude'])).kilometers
            if distance <= distance_threshold_km:
                merged_data.append({**row1, **row2, 'Distance (km)': distance})
            # else : 
            #     zero_list = {'Vehicle': None, 'Aid': None, 'Location': row1['Location'], 'Count': 0}
            #     merged_data.append({**zero_list, **row2, 'Distance (km)': distance})
    
    # Create a new DataFrame from the merged data
    merged_df = pd.DataFrame(merged_data)
    return merged_df

def transform_df(df_merged):
    df_merged['geometry_str'] = df_merged['geometry'].astype(str)
    total_aids_by_type = df_merged.groupby(['Aid', 'Vehicle','geometry_str'])['Count'].sum().reset_index()
    # total_aids_by_type['geometry'] = total_aids_by_type['geometry_str'].apply(wkt.loads)

    def join_lists(lst):
        return ', '.join(lst)

    test_df = total_aids_by_type.groupby(['geometry_str','Aid','Vehicle'])[['Count']].agg(int).reset_index()
    test_df['stats'] = test_df['Aid'] + " : " + test_df['Vehicle'] + " (" + test_df['Count'].astype(str) + ")"

    test_df = test_df.groupby(['geometry_str'])[['Aid','Vehicle','Count','stats']].agg(list).reset_index()
    test_df['Aid'] = test_df['Aid'].apply(join_lists)
    test_df['Vehicle'] = test_df['Vehicle'].apply(join_lists)
    test_df['Count'] = test_df['Count'].apply(sum)
    test_df['stats'] = test_df['stats'].apply(join_lists)
    test_df['geometry'] = test_df['geometry_str'].apply(wkt.loads)
    location_without_aid = df_merged[~df_merged['geometry'].isin(test_df['geometry'])][['Aid', 'Vehicle', 'Count', 'geometry']]
    location_without_aid['geometry_str'] = location_without_aid['geometry'].astype(str)
    location_without_aid['stats'] = 'No aid'
    location_without_aid = location_without_aid[['geometry_str', 'Aid', 'Vehicle', 'Count', 'stats', 'geometry']]
    location_without_aid
    result_df = pd.concat([test_df,location_without_aid])
    return result_df

def reduce_location_threshold(df_location, threshold = 5):

    # Sample data with a 'geometry' column containing Shapely Point objects

    gdf = gpd.GeoDataFrame(df_location, geometry='geometry')

    # # Create a DataFrame with coordinates
    # coordinates_df = gdf['geometry'].apply(lambda geom: (geom.x, geom.y)).apply(pd.Series)
    # coordinates_df.columns = ['longitude', 'latitude']

    # # Calculate the pairwise distances between points using cdist
    # distances = cdist(coordinates_df, coordinates_df, 'euclidean')

    # # Create a mask to filter out points that are less than 5 km apart
    # mask = (distances >= threshold) | (distances == 0)

    # # Apply the mask to the DataFrame
    # filtered_gdf = gdf[mask.any(axis=1)].reset_index(drop=True)

    # Create a DataFrame with coordinates
    coordinates_df = gdf['geometry'].apply(lambda geom: (geom.x, geom.y)).apply(pd.Series)
    coordinates_df.columns = ['longitude', 'latitude']

    # Calculate the pairwise distances between points using Haversine
    distances = pd.DataFrame(columns=coordinates_df.index, index=coordinates_df.index)

    for i in coordinates_df.index:
        for j in coordinates_df.index:
            distances.loc[i, j] = haversine((coordinates_df.at[i, 'latitude'], coordinates_df.at[i, 'longitude']),
                                            (coordinates_df.at[j, 'latitude'], coordinates_df.at[j, 'longitude']))

    # Create a mask to filter out points that are less than 5 km apart
    mask = (distances >= threshold) | (distances == 0)

    # Apply the mask to the DataFrame
    filtered_gdf = gdf[mask.any(axis=1)].reset_index(drop=True)

    return filtered_gdf