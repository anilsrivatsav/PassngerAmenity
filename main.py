import streamlit as st
from data_loader import DataLoader
from ui_renderer import render_station_table, render_station_card, render_work_table, render_work_cards

def run_app():
    st.set_page_config(page_title="Railway Dashboard", layout="wide")
    st.title("🚉 Railway Amenities Dashboard")

    station_csv = "stations.csv"
    works_csv = "works.csv"

    data_loader = DataLoader(station_csv, works_csv)
    station_data = data_loader.load_station_data()
    works_data = data_loader.load_works_data()

    st.sidebar.header("Navigation")
    page_mode = st.sidebar.radio("View", ["Station Details", "Works Details"])

    if page_mode == "Station Details":
        station_names = station_data["DISPLAY_NAME"].tolist()
        selected_station = st.sidebar.selectbox("Select a Station", station_names)
        station_details = station_data[station_data["DISPLAY_NAME"] == selected_station].iloc[0]
        render_station_card(station_details)

    elif page_mode == "Works Details":
        filters = st.sidebar.radio("Filter Works By", ["Station", "Year of Sanction", "Section"])
        if filters == "Station":
            selected_station = st.sidebar.selectbox("Select a Station", station_data["DISPLAY_NAME"])
            works_for_station = works_data[works_data["Station"] == selected_station.split("(")[0].strip()]
            render_work_table(works_for_station)
            render_work_cards(works_for_station)

run_app()