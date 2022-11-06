import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
import folium
import leafmap.foliumap as leafmap
import requests
import numpy as np
##Data
latlongs = pd.read_excel('./Data/bronze/stops_coordinates_general.xlsx')
dataframe= pd.read_excel('./Data/bronze/train_routes20.xlsx')
stations = pd.read_csv('./Data/bronze/stationsCleaned.csv')
dataframe.rename(columns={'Train number': 'trainnumber'}, inplace=True)
##Page config
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)





##First map

st.sidebar.title("About")
st.sidebar.info("In the map on the left it is possible to get an overview of the stations. By searching in the box it is possbible to filter per state")

st.title("Stations per region")


number = st.number_input('Insert a train number')
st.write('The current number is ', number)

import time
with st.spinner('Wait for it...'):
    time.sleep(5)
st.success('Done!')


c1,c2 = st.columns(2)

with c1:
    st.header("Stations in Belgium")
    p = leafmap.Map(center=[51.0362, 3.73373], zoom=8)


    p.add_points_from_xy(
        stations[['longitude','latitude']],
        x="longitude",
        y="latitude",
        
        icon_names=['gear', 'map', 'leaf', 'globe'],
        spin=True,
        add_legend=True,
    )
            
    p.to_streamlit(height=700)




##Second map

##Functions

with c2:
    st.header("Routes")
   
    def get_directions_response(lat1, long1, lat2, long2, mode='drive'):
        url = "https://route-and-directions.p.rapidapi.com/v1/routing"
        key = "5af3fbbb1dmsh16aff6a8e7e35e5p1cd880jsne9f8d69ef3d5"
        host = "route-and-directions.p.rapidapi.com"
        headers = {"X-RapidAPI-Key": key, "X-RapidAPI-Host": host}
        querystring = {"waypoints":f"{str(lat1)},{str(long1)}|{str(lat2)},{str(long2)}","mode":mode}
        response = requests.request("GET", url, headers=headers, params=querystring)
        return response


    def get_list_latlon(trainnumber):
        my_list = []
        rslt_df = dataframe.loc[(dataframe['trainnumber'] == trainnumber)]
        rslt_df.fillna(0)
        rslt_df.head(1)
        rslt_df = rslt_df.replace(0,np.nan).dropna(axis=1,how="all")
        for i in range(rslt_df.shape[1]-2):
            name = rslt_df['Stop ' + str(i+1)].values[0]
            coor = latlongs.loc[(latlongs['name'] == name)]
            cor = coor[['latitude', 'longitude']].head(1).values.reshape(-1)
            my_list.append(cor)
        return my_list


    def plot_train_route(number): 
        lat_lons = get_list_latlon(number) 
        responses = []
        for n in range(len(lat_lons)-1):
            lat1, lon1, lat2, lon2 = lat_lons[n][0], lat_lons[n][1], lat_lons[n+1][0], lat_lons[n+1][1]
            response = get_directions_response(lat1, lon1, lat2, lon2, mode='walk')
            responses.append(response)
        return responses


    def create_map(responses, lat_lons):

        df = pd.DataFrame()
        
        # add markers for the places we visit
        for point in lat_lons:
            folium.Marker(tuple(point)).add_to(m)
        # loop over the responses and plot the lines of the route
        for response in responses:
            mls = response.json()['features'][0]['geometry']['coordinates']
            points = [(i[1], i[0]) for i in mls[0]]
            
            # add the lines
            folium.PolyLine(points, weight=5, opacity=1).add_to(m)
            temp = pd.DataFrame(mls[0]).rename(columns={0:'Lon', 1:'Lat'})[['Lat', 'Lon']]
            df = pd.concat([df, temp])
        # create optimal zoom
        sw = df[['Lat', 'Lon']].min().values.tolist()
        sw = [sw[0]-0.0005, sw[1]-0.0005]
        ne = df[['Lat', 'Lon']].max().values.tolist()
        ne = [ne[0]+0.0005, ne[1]+0.0005]
        m.fit_bounds([sw, ne])






    m = folium.Map(location=[51.0500, 3.7303], zoom_start=8)
    # call to render Folium map
    number = 12408
    responses = plot_train_route(number)
    lat_lons = get_list_latlon(number)
    create_map(responses, lat_lons)
    st_data = st_folium(m, width=725 )

   




