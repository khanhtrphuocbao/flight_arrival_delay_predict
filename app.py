import streamlit as st

st.set_page_config(page_title="Reporting-Airline Ontime Performance", layout='wide',
                   page_icon=':airplane:')

st.markdown('# Reporting-Airline Ontime Performance')
st.image('assets/images/airport.jpg', use_column_width=True)
st.markdown("""
Reporting carriers are required to (or voluntarily) report on-time data
for flights they operate: on-time arrival and departure data 
for non-stop domestic flights by month and year, by carrier 
and by origin and destination airport. Includes scheduled and actual departure and arrival times, 
causes of delay and cancellation, air time, and non-stop distance.""")