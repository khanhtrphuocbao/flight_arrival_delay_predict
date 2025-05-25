import streamlit as st
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff


from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, StandardScaler



#---------------------------- [ PAGE SETUP ] ----------------------------
# Setting the page title, layout, icon and initial sidebar state.

st.set_page_config(page_title="Reporting-Airline Ontime Performance", layout='wide',
                   page_icon=':airplane:', initial_sidebar_state='collapsed')

reduce_header_height_style = """
    <style>
        div.block-container {padding-top : 1rem;}
        ul.streamlit-expander {border-width: 2px !important; border-radius: .5rem;}
    </style>
"""
st.markdown(reduce_header_height_style, unsafe_allow_html=True)

sns.set(font_scale=.5)

@st.cache
def get_data(path):
    return pd.read_csv(path, parse_dates=['FlightDate'])


df = get_data('./data/cleaned/2022_full.csv')

df_ft=df[(df['ArrDelay'] <= 150) 
        & (df['FlightDate'] <= '2022-01-20')
].drop(['Avg_Delay'], axis=1)

df_ft=df_ft[['DayOfWeek', 'FlightDate', 'Reporting_Airline', 'Dest', 
            'CRSDepTime', 'DepTime', 'DepDelay', 'CRSArrTime', 'ArrTime',
    'CRSElapsedTime', 'AirTime', 'Distance', 'ArrDelay']]


st.markdown('# Reporting-Airline Ontime Performance')
st.markdown("""## **Model** - predict delay time at arrival""")



    
train = df_ft[(df_ft['FlightDate'] < '2022-01-15')]
test = df_ft[(df_ft['FlightDate'] >= '2022-01-15')&(df_ft['FlightDate'] <= '2022-01-20')]

features, target = ['DepDelay', 'DepTime'], 'ArrDelay'

x_train, x_test = train[features], test[features]
y_train, y_test= train[target], test[target]


pipe = Pipeline([
    # ('scaler', MinMaxScaler()),
    ('model', LinearRegression())    
    ])
pipe.fit(x_train, y_train)
y_pred = pipe.predict(x_test)

with st.expander("", True):
    col1, col2, col3 = st.columns(3)
    col1.markdown("### Prediction")

    with col2:
        depdelay = st.slider('Delay at departure',-50, 150)

    with col3:
        deptime = st.time_input('Departure time')

    res = pipe.predict([[depdelay, deptime.hour * 60 + deptime.minute]])

    st.metric('Predicted arrival delay', f'{round(res[0],4)} mins')





st.markdown("### Feature selection")
# col1, col2 = st.columns([2,1])

st.write("**Numerical variables**")






with st.expander("Heatmap and Delay-time distribution", False):
    col1, col2, = st.columns(2)

    with col1:

        corr = df.drop(['Avg_Delay', 'Reporting_Airline', 'Dest',], axis=1)[['DayOfWeek',  
                'CRSDepTime', 'DepTime', 'DepDelay', 'CRSArrTime', 'ArrTime',
        'CRSElapsedTime', 'AirTime', 'Distance', 'ArrDelay']].corr()
        mask = np.triu(np.ones_like(corr))

        fig, ax = plt.subplots()
        sns.heatmap(corr, mask=mask, annot=True)
        st.write(fig)

    with col2:

        hist_data = df[['ArrDelay','DepDelay']].to_numpy().T
        group_labels = ['ArrDelay','DepDelay']

        figejemplo = ff.create_distplot(hist_data, group_labels,  show_hist=True, show_rug=False)

        st.plotly_chart(figejemplo, use_container_width=True)

    





with st.expander("after removing unexpected values (`DepDelay` > 150 mins)", False):
    col1, col2 = st.columns(2)
    with col1:
    

        fig, ax = plt.subplots()
        sns.heatmap(df_ft.drop(['Reporting_Airline', 'Dest', ], axis=1).corr(), mask=mask, annot=True)
        st.write(fig)
    with col2:
        hist_data = df_ft[['ArrDelay','DepDelay']].to_numpy().T
        group_labels = ['ArrDelay','DepDelay']

        figejemplo = ff.create_distplot(hist_data, group_labels,  show_hist=True, show_rug=False)

        st.plotly_chart(figejemplo, use_container_width=True)

df_ft['isWeekday'] = df_ft['DayOfWeek'] < 6

with st.expander("Categorical variable", False):
    col1, col2 = st.columns(2)
    with col1:

    # col1, col2 = st.columns(2)
    # with col1:
        st.write("ArrDelay in weekday and weekend")
        fig, ax = plt.subplots()
        sns.boxplot(data=df_ft, y='ArrDelay', x='isWeekday')
        st.write(fig)
    with col2:
        st.write("ArrDelay per airline")
        fig, ax = plt.subplots()
        sns.boxplot(data=df_ft, x='ArrDelay', y='Reporting_Airline', orient='h')
        st.write(fig)



st.markdown("### Modeling and Evaluation")
with st.expander("Multivariate Linear Regression", False):

    


    st.markdown("""Features: `DepDelay`, `DepTime`    Target variable: `ArrDelay`""")

    st.markdown("""Train set: flight from 01 - 14/01/2022

Test set: flight from 15 - 20/01/2022""")



    col1, col2 = st.columns(2)


    with col1:


        fig, ax = plt.subplots()
        sns.regplot(x=y_pred, y=y_test)
        ax.set(xlabel='fitted value', ylabel='actual value')
        plt.legend()
        st.write(fig)

    
    with col2:
        fig, ax = plt.subplots()
        sns.distplot(y_pred, hist=False, color='r', label='fitted value')
        sns.distplot(y_test, hist=False, color='b', label='actual value')
        plt.legend()
        st.write(fig)

with st.expander("", True):
    
    st.write('### Evaluation')

    col1, col2, col3, col4 = st.columns(4)

    from sklearn.metrics import mean_absolute_error,mean_squared_error
  
    mae = mean_absolute_error(y_true=y_test,y_pred=y_pred)
    mse = mean_squared_error(y_true=y_test,y_pred=y_pred)
    rmse = mean_squared_error(y_true=y_test,y_pred=y_pred,squared=False)
    r2 = pipe.score(x_test, y_test)

    col1.metric("MAE", round(mae,4))
    col2.metric("MSE", round(mse, 4))
    col3.metric("RMSE", round(rmse,4))
    col4.metric("R2", round(r2,4))




