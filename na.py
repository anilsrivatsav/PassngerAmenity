import os
import pandas as pd
import logging
import streamlit as st

# Configure logging
logging.basicConfig(
    filename="chatbot_debug.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class RailwayAmenitiesChatbot:
    def __init__(self, station_csv: str = "stations.csv", works_csv: str = "works.csv"):
        self.station_csv = station_csv
        self.works_csv = works_csv
        try:
            logging.info("Loading station CSV data...")
            self.station_data = pd.read_csv(self.station_csv)
            logging.info("Station data loaded successfully.")
            self._prepare_station_data()

            logging.info("Loading works CSV data...")
            self.works_data = pd.read_csv(self.works_csv)
            logging.info("Works data loaded successfully.")
            self._normalize_works_data()

        except Exception as e:
            logging.error(f"Failed to load or process data: {e}")
            raise

    def _prepare_station_data(self):
        """Normalize and clean station data."""
        self.station_data.columns = [
            col.strip().upper().replace(" ", "_") for col in self.station_data.columns
        ]
        self.station_data.fillna("", inplace=True)
        self.station_data["DISPLAY_NAME"] = self.station_data.apply(
            lambda row: f"{row['STATION_NAME']} ({row['STATION_CODE']})", axis=1
        )

    def _normalize_works_data(self):
        """Normalize works data to handle multiple stations in the same row."""
        self.works_data.columns = [
            col.strip().upper().replace(" ", "_") for col in self.works_data.columns
        ]
        self.works_data.fillna("", inplace=True)
        expanded_rows = []
        for _, row in self.works_data.iterrows():
            stations = str(row["STATION"]).split(",")
            for station in stations:
                station = station.strip()
                new_row = row.copy()
                new_row["STATION"] = station
                expanded_rows.append(new_row)
        self.works_data = pd.DataFrame(expanded_rows)

    def get_station_names(self):
        """Return a list of station display names."""
        return self.station_data["DISPLAY_NAME"].tolist()

    def get_station_details(self, station_name):
        """Retrieve details for a selected station."""
        try:
            station_code = station_name.split("(")[-1].strip(")")
            station_row = self.station_data[self.station_data["STATION_CODE"] == station_code]
            if not station_row.empty:
                return station_row.iloc[0].to_dict()
            else:
                return None
        except Exception as e:
            logging.error(f"Error retrieving station details: {e}")
            return None

    def get_station_works(self, station_name):
        """Retrieve works for the selected station."""
        try:
            station_works = self.works_data[self.works_data["STATION"] == station_name]
            return station_works
        except Exception as e:
            logging.error(f"Error retrieving works for station: {e}")
            return pd.DataFrame()

    def filter_works(self, query=None, year=None, section=None):
        """Filter works by query, year, or section."""
        filtered_data = self.works_data
        if query:
            filtered_data = filtered_data[
                filtered_data["SHORT_NAME_OF_WORK"].str.contains(query, case=False, na=False)
            ]
        if year:
            filtered_data = filtered_data[filtered_data["YEAR_OF_SANCTION"] == year]
        if section:
            filtered_data = filtered_data[filtered_data["SECTION"] == section]
        return filtered_data


def render_station_details(station_details):
    """Render station details."""
    st.markdown(
        f"""
        <div style='background: #fff; border: 1px solid #ddd; border-radius: 10px; padding: 20px; margin: 20px 0;'>
            <h3 style='text-align: center;'>🚉 {station_details['STATION_NAME']} ({station_details['STATION_CODE']})</h3>
            <p><b>Category:</b> {station_details['CATEGORISATION']}</p>
            <p><b>Earnings Range:</b> {station_details['EARNINGS_RANGE']}</p>
            <p><b>Passenger Range:</b> {station_details['PASSENGER_RANGE']}</p>
            <p><b>Platforms:</b> {station_details['PLATFORMS']} ({station_details['PLATFORM_TYPE']})</p>
            <p><b>Parking Available:</b> {station_details['PARKING']}</p>
            <p><b>Pay-and-Use Toilets:</b> {station_details['PAY-AND-USE']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_work_cards(works_data):
    """Render works in a card view."""
    st.markdown(
        """
        <style>
            .grid-container {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 20px;
                padding: 10px;
            }}
            .work-card {{
                background: #FFF;
                border: 1px solid #DDD;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            }}
            .work-card h4 {{
                font-size: 1.2rem;
                color: #333;
            }}
            .work-card p {{
                font-size: 1rem;
                margin: 5px 0;
                color: #555;
            }}
        </style>
        <div class="grid-container">
        """,
        unsafe_allow_html=True,
    )
    for _, row in works_data.iterrows():
        st.markdown(
            f"""
            <div class="work-card">
                <h4>🛠 {row.get('SHORT_NAME_OF_WORK', 'N/A')}</h4>
                <p><b>Project ID:</b> {row.get('PROJECTID', 'N/A')}</p>
                <p><b>Current Cost:</b> {row.get('CURRENT_COST', 'N/A')}</p>
                <p><b>Remarks:</b> {row.get('REMARKS', 'N/A')}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def run_chatbot_app():
    st.set_page_config(page_title="Amenities Dashboard", layout="wide")
    st.title("🚉 Railway Amenities Dashboard")

    station_csv = "stations.csv"
    works_csv = "works.csv"

    if not os.path.exists(station_csv) or not os.path.exists(works_csv):
        st.error(f"CSV files '{station_csv}' or '{works_csv}' not found.")
        return

    try:
        chatbot = RailwayAmenitiesChatbot(station_csv, works_csv)

        # Tabs for Station-Based and Works-Based Views
        tab1, tab2 = st.tabs(["🔍 Station-Based View", "🛠 Works-Based View"])

        # Station-Based View
        with tab1:
            search_query = st.text_input("Search Station by Name or Code")
            station_names = chatbot.get_station_names()
            matching_stations = [name for name in station_names if search_query.lower() in name.lower()]
            selected_station = st.selectbox("Matching Stations", matching_stations)

            if selected_station:
                station_details = chatbot.get_station_details(selected_station)
                if station_details:
                    render_station_details(station_details)

                works_data = chatbot.get_station_works(selected_station.split("(")[-1].strip(")"))
                st.subheader("Works")
                if st.checkbox("View as Cards"):
                    render_work_cards(works_data)
                else:
                    st.dataframe(works_data)

        # Works-Based View
        with tab2:
            st.subheader("All Works")
            filter_query = st.text_input("Search by Short Name of Work, Section, or Year")
            filtered_works = chatbot.filter_works(query=filter_query)
            if st.checkbox("View as Cards"):
                render_work_cards(filtered_works)
            else:
                st.dataframe(filtered_works)

    except Exception as e:
        logging.error(f"Error running chatbot app: {e}")
        st.error(f"An error occurred: {e}")


if __name__ == "__main__":
    run_chatbot_app()