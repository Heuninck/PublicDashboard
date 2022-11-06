import pickle
from pathlib import Path
import plost
import pandas as pd  # pip install pandas openpyxl
import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit
import streamlit_authenticator as stauth  # pip install streamlit-authenticator
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt



# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="NMBS-Belgium", page_icon=":bar_chart:", layout="wide")

##Import DATA
facilities = pd.read_csv("./Data/bronze/facilitiesCleaned.csv", index_col=0)
satisfaction = pd.read_csv("./Data/bronze/satisfactionCleaned.csv", index_col=0)
stations = pd.read_csv("./Data/bronze/stationsCleaned.csv", index_col=0)
stops = pd.read_csv("./Data/bronze/stopsCleaned.csv", index_col=0)
all_trips = pd.read_csv("./Data/bronze/all_tripsCleaned.csv", index_col=0)
incidents = pd.read_csv("./Data/bronze/incidentsCleaned.csv", index_col=0)
travelers= pd.read_csv("./Data/bronze/travelersCleaned.csv", index_col=0)
delayedtrips = all_trips

dep_delay_secs = all_trips['departure delay']
ontime = dep_delay_secs[(dep_delay_secs==0)]

# --- USER AUTHENTICATION ---
names = ["Stijn Heuninck", "Rebecca Miller"]
usernames = ["Manager-nmbs", "rmiller"]
##Wachtwoord: abc123

##Spinner 

import time
with st.spinner('Wait for it...'):
    time.sleep(5)
st.success('Done!')

# load hashed passwords
file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
    "sales_dashboard", "abcdef", cookie_expiry_days=5)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status == True:

    # ---- SIDEBAR ----
    authenticator.logout("Logout", "sidebar")
    st.sidebar.title(f"Welcome {name}")
    st.sidebar.header("Please Filter Here:")
    

    # Functions & DATA
    avgdelay = all_trips['arrival delay'].mean()


    @st.cache
    def Get_arrivaldelays(name):
        return all_trips[all_trips['Railway operators'] == name]['arrival delay'].mean()

    @st.cache   
    def Get_departuredelays(name):
        return all_trips[all_trips['Railway operators'] == name]['departure delay'].mean()

    @st.cache
    def Get_meansatisfaction():
        return str(int(satisfaction['Avg Satisfaction'].mean()))

    @st.cache
    def Get_meandelay():
        return str(int(delayedtrips['departure delay'].mean()))

    @st.cache
    def Get_trainsontime():
        return str(round(len(ontime)/dep_delay_secs.shape[0], 2)) 

    @st.cache
    def Get_delays():
        delay_dep = all_trips['departure delay']
        delayeddep = delay_dep[delay_dep>=0]

        delayeddep = pd.Series(delayeddep, dtype=np.int64, name='delay')
        outliers = delayeddep[delayeddep>=7200]
        delayed = delayeddep[delayeddep<7200]
        return delayed

   


    # Functions & dashboard
    

    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        
    


    st.sidebar.subheader('Satisfaction per day')
    time_hist_color = st.sidebar.selectbox('Color by', ('departure delay', 'arival delay')) 

    st.sidebar.subheader('Delay per operator')
    donut_theta = st.sidebar.selectbox('Select data', ('arrival delay','departure delay'))

    st.sidebar.subheader('Line chart parameters')
    plot_data = st.sidebar.multiselect('Select data', ['departure delay', 'arrival delay'], ['departure delay', 'arrival delay'])
    plot_height = st.sidebar.slider('Specify plot height', 200, 500, 250)

    


    # Row A
    st.markdown('### Metrics')
    col1, col2, col3 = st.columns(3)
    col1.metric("Avg satisfaction", Get_meansatisfaction()+"%")
    col2.metric("Avg delay time in seconds", Get_meandelay())
    col3.metric("Percentages of trains on time", Get_trainsontime())




    


    #row b
    c1, c2= st.columns((6,4))
    with c1:
        st.markdown('### Evolution of delay')
        df  = pd.read_csv("./Data/bronze/heatmap1.csv", index_col=0)

        fig, ax = plt.subplots()

        x_axis_labels = [4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]# labels for x-axis
        y_axis_labels = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']# labels for y-axis

        # create seabvorn heatmap with required labels
        sns.heatmap(df, xticklabels=x_axis_labels, yticklabels=y_axis_labels, cmap="YlGnBu")
        st.write(fig)
    with c2:
        
        st.markdown('### Delay per operator')
        plost.donut_chart(
            data= pd.DataFrame({"names":['SNCB/NMBS', 'EUROSTARFR', 'THI-FACT'],"arrival delay":[Get_arrivaldelays('EUROSTARFR'), Get_arrivaldelays('SNCB/NMBS'), Get_arrivaldelays('THI-FACT')], "departure delay":[Get_departuredelays('EUROSTARFR'), Get_departuredelays('SNCB/NMBS'), Get_departuredelays('THI-FACT')]}),
            theta=donut_theta,
            color='names',
            legend='bottom', 
            use_container_width=True)


        
        

    # Row C

    c1, c2 = st.columns((6,4))
    with c1:
        TimeSeries = all_trips[['Date of departure','departure delay', 'arrival delay']]
        df = TimeSeries.groupby("Date of departure").mean()
        df= df.reset_index()
        data = pd.DataFrame({"Date of departure"})
        st.markdown('### Delay over time')

        st.line_chart(df, x = 'Date of departure', y = plot_data, height = plot_height)


    with c2:
        st.markdown('### Delay distribution')
        st.bar_chart(Get_delays()/60)







        # ---- HIDE STREAMLIT STYLE ----
    hide_st_style = """
                    <style>
                    #MainMenu {visibility: hidden;}
                    footer {visibility: hidden;}
                    header {visibility: hidden;}
                    </style>
                    """
    st.markdown(hide_st_style, unsafe_allow_html=True)