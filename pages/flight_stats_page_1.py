import streamlit as st
import plotly.express as px
import pandas as pd
import datetime
from numerize.numerize import numerize

import folium
import airportsdata
from streamlit_folium import st_folium
from folium.features import DivIcon



#---------------------------- [ PAGE SETUP ] ----------------------------
# Setting the page title, layout, icon and initial sidebar state.

st.set_page_config(page_title="Reporting-Airline Ontime Performance", layout='wide',
                   page_icon=':airplane:', initial_sidebar_state='collapsed')

reduce_header_height_style = """
    <style>
        ul.streamlit-expander {border-width: 2px !important; border-radius: .5rem;}
        div.streamlit-expanderHeader p {font-size: 20px;}
    </style>
"""
st.markdown(reduce_header_height_style, unsafe_allow_html=True)


@st.cache
def get_data(path):
    return pd.read_csv(path, parse_dates=['FlightDate'])


df_cleaned = get_data('./data/cleaned/2022.csv')





#---------------------------- [ FILTER ] ----------------------------


# Allowing the user to select the airline and the date range.
col1, col2 = st.columns([5,1])
with col1:
    st.markdown('# Reporting-Airline Ontime Performance')
with col2:
    with st.expander("Filter data", False):

        airline = st.multiselect(
            "Airline:",
            options=df_cleaned["Reporting_Airline"].unique(),
            default=df_cleaned["Reporting_Airline"].unique()
        )

        d_start = st.date_input(
            "Start date:",
            datetime.date(2022, 1, 1),
            min_value=datetime.date(2022, 1, 1),
            max_value=datetime.date(2022, 3, 15))

        d_end = st.date_input(
            "End date:",
            datetime.date(2022, 3, 15),
            min_value=datetime.date(2022, 1, 1),
            max_value=datetime.date(2022, 3, 15))

# year = st.sidebar.slider(
#      'Select a range of Year:',
#      2011, 2016, (2014, 2016))
# st.sidebar.write('Values:', year)



#---------------------------- [ DATA FILTERING ] ----------------------------


df_cleaned_selection = df_cleaned.query(
    "Reporting_Airline == @airline & @d_start <= FlightDate <= @d_end "
)

df_code = df_cleaned_selection[['CarrierDelay', 'WeatherDelay', 'NASDelay', 'SecurityDelay',
                                'LateAircraftDelay']]

sum_delay = pd.DataFrame(df_code.sum(), columns=['minute']).reset_index()
df_code = df_code.fillna(0)

count = [[col, df_code[df_code[col] > 0].count()[0]]
         for col in df_code.columns]
count_cause = pd.DataFrame(data=count, columns=['Cause', 'Count'])



#---------------------------- [ HEADER ] ----------------------------

st.markdown('## Flight Stats')
with st.expander("Flight count over time", True):




#---------------------------- [ TIME PLOT ] ----------------------------


    col0 = st.columns(1)
    

    flight_count = df_cleaned_selection[['FlightDate', 'Avg_Delay']].groupby(
        'FlightDate').count().reset_index()
    fig = px.line(flight_count, x='FlightDate', y="Avg_Delay",
                labels={"FlightDate": "Date",
                    "Avg_Delay": "Flight count"},)
    # fig.update_traces(line_color='black')

    col0[0].plotly_chart(fig, use_container_width=True)

#---------------------------- [ DATA OVERVIEW ] ----------------------------

with st.expander("**Overview**",expanded=True):


    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 2, 1])


    col1.metric("Observed days",
                f"{d_start.strftime('%d/%m/%y')} - {d_end.strftime('%d/%m/%y')}", (d_end-d_start).days, 'off')

    col2.metric("Number of flight", numerize(df_cleaned_selection.shape[0]))

    col3.metric("Number of Airline",
                df_cleaned_selection["Reporting_Airline"].nunique())

    col4.metric("Total airtime",
                f"{round(df_cleaned_selection['AirTime'].sum()/60/24, 2)} days")

    col5.metric("Avg airtime",
                f"{round(df_cleaned_selection['AirTime'].mean()/60, 2)} hours")



    col1.metric("Avg delay rate (t > 5 mins)",
                f"{round(df_cleaned_selection[df_cleaned_selection['Avg_Delay'] > 5].shape[0]/df_cleaned_selection.shape[0]*100, 2)}%")

    col2.metric("Distance",
                f"{numerize(round(df_cleaned_selection['Distance'].sum()*1.609344, 2))} km")

    col3.metric("Avg distance",
                f"{round(df_cleaned_selection['Distance'].mean()*1.609344, 2)} km")


    col4.metric("Total delay",
                f"{round(df_cleaned_selection['Avg_Delay'].sum()/60/24, 2)} days")

    col5.metric("Avg delay",
                f"{round(df_cleaned_selection['Avg_Delay'].mean(), 2)} mins")


#---------------------------- [ ROW 1 ] ----------------------------




airlines = pd.read_csv('./data/L_UNIQUE_CARRIERS.csv',
                       names=['CODE', 'AIRLINE'])

c2airline = airlines.set_index('CODE')['AIRLINE'].to_dict()

stats = df_cleaned_selection['Avg_Delay'].groupby(
                df_cleaned_selection['Reporting_Airline']
            ).describe()[['count', 'mean', 'min', 'max']].sort_values(
                    by='count', ascending=False).reset_index()




col1, col2, col3 = st.columns([4, 7, 5])

with col1:
    with st.expander("**Cause of Delay**",True):
        fig=px.pie(
                sum_delay,
                values='minute',
                names='index',
                template='plotly_white',
                title='total delay time (minute)',
                hole=.4,
                color_discrete_sequence=px.colors.cyclical.IceFire[::3],
            )
        fig.update_layout(legend = dict(font = dict(size = 8)),
                    legend_title = dict(font = dict(size = 8)))
        st.plotly_chart(fig, use_container_width=True)





with col2:

    st.write('**No. flights per Airline**')


    fig = px.bar(
            stats,
            y='Reporting_Airline',
            x='count',
            color='Reporting_Airline',
            labels={"Reporting_Airline": "Airline",
                    "count": "Flight count"},
            orientation='h',
            template='plotly_white',
            color_discrete_sequence=px.colors.cyclical.IceFire
        )


    newnames = {t: c2airline[t] for t in stats['Reporting_Airline'].unique()}
    fig.for_each_trace(lambda t: t.update(name = newnames[t.name],
                                    legendgroup = newnames[t.name],
                                    hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])
                                    )
                )

    col2.plotly_chart(fig, use_container_width=True)



with col3:

    st.write('**Mean delay per Airline**')


    col_2_bar = px.bar(
        stats,
        y='Reporting_Airline',
        x='mean',
        labels={"Reporting_Airline": "Airline",
                "mean": "Mean delay (minute)"},
        color='Reporting_Airline',
        orientation='h',
        template='plotly_white',
        color_discrete_sequence=px.colors.cyclical.IceFire
    )

    col_2_bar.update_layout(showlegend=False)
    col3.plotly_chart(col_2_bar, use_container_width=True)




#---------------------------- [ ROW 2 ] ----------------------------

with st.expander("**Delay Analysis**", True):
    col2, col3 = st.columns(2)


    with col2:

        st.write('**Delay level per Airline**')
        colors = px.colors.cyclical.IceFire[1::2]
        colors_a=colors[:3]
        
        fig = px.histogram(
            df_cleaned_selection,
            y='Reporting_Airline',
            # names='Name',
            color='Delay_Level',
            template='plotly_white',
            labels={"count": "flight count",
                    "Reporting_Airline": "Airline"},
            color_discrete_sequence=colors_a[::-1],
        )

        newnames = {'0':'on time (t < 5 min)', '1': 'small delay (5 < t < 45 min)', '2': 'large delay (t > 45 min)'}
        fig.for_each_trace(lambda t: t.update(name = newnames[t.name],
                                        legendgroup = newnames[t.name],
                                        hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])
                                        )
                    )
        fig.update_layout(xaxis_title="flight count")
        
        col2.plotly_chart(fig, use_container_width=False)

    mean = df_cleaned_selection[['DepDelay', 'ArrDelay']].groupby(
        df_cleaned_selection['Reporting_Airline']).mean().reset_index()



    with col3:
        st.write('**DEP delay vs. ARR delay**')


        fig = px.histogram(
            mean,
            x=['DepDelay', 'ArrDelay'],
            y='Reporting_Airline',
            # names='Name',
            template='plotly_white', barmode='group',
            labels={"Reporting_Airline": "Airline"},
            color_discrete_sequence=colors_a[::-1]
        )
        fig.update_layout(legend_title='', xaxis_title="average delay time (minute)")
        col3.plotly_chart(fig, use_container_width=False)

#---------------------------- [ ROW 3 - AIRLINE ] ----------------------------


st.markdown('### Airline performance')
with st.expander("Filter airline", True):
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_airline = st.selectbox(
            "Airline:",
            options=df_cleaned["Reporting_Airline"].unique(),
        )
    with col2:
        d_start_selected = st.date_input(
            "Start date:",
            d_start,
            min_value=d_start,
            max_value=d_end,
            key='2',)

    with col3:
        d_end_selected = st.date_input(
            "End date:",
            d_end,
            min_value=d_start,
            max_value=d_end,
            key='3',)

df_airline_selection = df_cleaned_selection.query(
    "Reporting_Airline == @selected_airline & @d_start_selected <= FlightDate <= @d_end_selected "
)






airports = airportsdata.load('IATA')

def draw_map(df):
    """ Return a folium.Map() object represents flights of selected airport.
    """

    df_count=df.groupby(['Origin', 'Dest']).size().reset_index(name='counts')

    m = folium.Map(location=[39.198744, -102.083682],  width=750, height=500)
    m.fit_bounds([[45, -125], [24, -60]])

    for i in range(df_count.shape[0]):
        
        
        try:
            lat1, lon1,lat2, lon2=airports[df_count.iloc[i][0]]['lat'], airports[df_count.iloc[i][0]]['lon'], airports[df_count.iloc[i][1]]['lat'],  airports[df_count.iloc[i][1]]['lon']
            folium.PolyLine([[lat1, lon1],  [lat2, lon2]],weight = 0.2).add_to(m)
        except:
            pass
    list_airport=[*list(df_count['Origin']), *list(df_count['Dest'])]
    airport=set(list_airport)
    for i in airport:
        try:
            folium.map.Marker(
                [airports[i]['lat'], airports[i]['lon']],
                icon=DivIcon(
                    icon_size=(250,36),
                    icon_anchor=(0,0),
                    html='<div style="font-size: 8pt">'+i+'</div>',
                    )
                ).add_to(m)
        except:
            pass

    return m


with st.expander("", True):

    st.markdown(f"### {selected_airline} - {c2airline[selected_airline]} performance ({d_start_selected.strftime('%d/%m/%y')} - {d_end_selected.strftime('%d/%m/%y')})")
    
    
    st.write("")


    col0, col1, col2 = st.columns([1, 2, 6])

    col1.metric("Delay rate", 
        f"{round(df_airline_selection[df_airline_selection['Avg_Delay'] > 5].shape[0]/df_airline_selection.shape[0]*100, 2)}%")
        
    col1.metric("Number of flight", numerize(df_airline_selection.shape[0]))

    col1.metric("Avg delay",
        f"{round(df_airline_selection['Avg_Delay'].mean(), 2)} mins")

    with st.spinner(""):


        with col2:
            map = draw_map(df_airline_selection)

            st_folium(map,width=750, height=500)