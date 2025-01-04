import os
import pandas as pd
import logging
import streamlit as st
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    filename="chatbot_debug.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load environment variables
load_dotenv()

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
        expanded_rows = []
        for _, row in self.works_data.iterrows():
            stations = str(row["Station"]).split(",")
            for station in stations:
                station = station.strip()
                new_row = row.copy()
                new_row["Station"] = station
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
            station_works = self.works_data[self.works_data["Station"] == station_name]
            return station_works
        except Exception as e:
            logging.error(f"Error retrieving works for station: {e}")
            return pd.DataFrame()

def render_station_table(station_data):
    """Render station data in a table view."""
    if station_data.empty:
        st.warning("No station details available.")
    else:
        st.dataframe(station_data)

def render_station_card(station_details):
    """Render station details in a modern and organized card format."""
    st.markdown(
        f"""
        <style>
            .station-card {{
                background: #FFF;
                border: 1px solid #DDD;
                border-radius: 15px;
                padding: 25px;
                margin: 20px 0;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            }}
            .station-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
            }}
            .station-card h3 {{
                color: #333;
                margin-bottom: 10px;
                font-size: 1.8rem;
                font-weight: 600;
                text-align: center;
            }}
            .station-card .header-line {{
                height: 4px;
                background-color: #007BFF;
                margin: 10px 0 20px 0;
                border-radius: 2px;
            }}
            .station-info {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
            }}
            .station-info p {{
                font-size: 1rem;
                margin: 5px 0;
                color: #555;
            }}
            .station-info b {{
                color: #333;
                font-weight: 600;
            }}
        </style>
        <div class="station-card">
            <h3>🚉 Station Details: {station_details['STATION_NAME']} ({station_details['STATION_CODE']}) - {station_details['CATEGORISATION']}</h3>
            <div class="header-line"></div>
            <div class="station-info">
                <p><b>Earnings Range:</b> {station_details['EARNINGS_RANGE']}</p>
                <p><b>Passenger Range:</b> {station_details['PASSENGER_RANGE']}</p>
                <p><b>Passenger Footfall:</b> {station_details['PASSENGER_FOOTFALL']}</p>
                <p><b>Platforms:</b> {station_details['PLATFORMS']}</p>
                <p><b>Platform Type:</b> {station_details['PLATFORM_TYPE']}</p>
                <p><b>Parking:</b> {station_details['PARKING']}</p>
                <p><b>Pay-and-Use Toilets:</b> {station_details['PAY-AND-USE']}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_work_table(work_data):
    """Render works data in a table view."""
    if work_data.empty:
        st.warning("No works found.")
    else:
        st.dataframe(work_data)

def render_work_cards(work_data):
    """Render works data in a grid layout with enhanced card styling."""
    if work_data.empty:
        st.warning("No works found.")
        return

    st.markdown(
        """
        <style>
            .card-container {
                display: flex;
                flex-wrap: wrap;
                justify-content: space-around;
                gap: 20px;
                margin-top: 20px;
            }
            .card {
                border: 1px solid #ddd;
                border-radius: 15px;
                background: linear-gradient(to bottom, #f8f9fa, #ffffff);
                padding: 20px;
                box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
                width: 30%;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 12px 24px rgba(0, 0, 0, 0.3);
            }
            .card h3 {
                font-size: 1.5rem;
                color: #333;
                margin-bottom: 10px;
                text-align: center;
                border-bottom: 2px solid #007BFF;
                padding-bottom: 5px;
            }
            .card p {
                font-size: 1rem;
                color: #555;
                margin: 8px 0;
            }
            .card p b {
                color: #007BFF;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    for _, row in work_data.iterrows():
        st.markdown(
            f"""
            <div class="card">
                <h3>{row.get('Short Name of Work', 'No Title')}</h3>
                <p><b>📅 Year of Sanction:</b> {row.get('Year of Sanction', 'N/A')}</p>
                <p><b>💰 Current Cost:</b> {row.get('Current Cost', 'N/A')}</p>
                <p><b>📊 Financial Progress:</b> {row.get('Financial Progress', 'N/A')}</p>
                <p><b>📝 Remarks:</b> {row.get('Remarks as on 14/06/24', 'N/A')}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

def run_chatbot_app():
    st.set_page_config(page_title="Amenities Dashboard", layout="wide")
    st.title("🚉 Amenities Dashboard")
    st.markdown("Find detailed information about railway stations and their associated works.")

    station_csv = "stations.csv"
    works_csv = "works.csv"

    if not os.path.exists(station_csv) or not os.path.exists(works_csv):
        st.error(f"CSV files '{station_csv}' or '{works_csv}' not found.")
        return

    try:
        chatbot = RailwayAmenitiesChatbot(station_csv, works_csv)

        st.sidebar.header("View Options")
        page_mode = st.sidebar.radio("Select View", ["Station Details", "Works Details"])

        if page_mode == "Station Details":
            station_names = chatbot.get_station_names()
            selected_station = st.sidebar.selectbox("Select a Station", station_names)
            if selected_station:
                station_details = chatbot.get_station_details(selected_station)
                st.subheader(f"Station Details: {selected_station}")
                render_station_card(station_details)

        elif page_mode == "Works Details":
            works_filter_mode = st.sidebar.radio(
                "Filter Works By", ["Station", "Year of Sanction", "Section"]
            )
            view_mode = st.radio("View Mode", ["Row View", "Card View"], index=0)  # On the right dashboard

            if works_filter_mode == "Station":
                station_names = chatbot.get_station_names()
                selected_station = st.sidebar.selectbox("Select a Station", station_names)
                if selected_station:
                    station_code = selected_station.split("(")[-1].strip(")")
                    works_data = chatbot.get_station_works(station_code)
                    st.subheader(f"Works for Station: {selected_station}")
                    if view_mode == "Row View":
                        render_work_table(works_data)
                    elif view_mode == "Card View":
                        render_work_cards(works_data)

            elif works_filter_mode == "Year of Sanction":
                years = sorted(chatbot.works_data["Year of Sanction"].dropna().unique())
                selected_year = st.sidebar.selectbox("Select a Year", years)
                if selected_year:
                    year_works_data = chatbot.works_data[
                        chatbot.works_data["Year of Sanction"] == selected_year
                    ]
                    st.subheader(f"Works Sanctioned in {selected_year}")
                    if view_mode == "Row View":
                        render_work_table(year_works_data)
                    elif view_mode == "Card View":
                        render_work_cards(year_works_data)

            elif works_filter_mode == "Section":
                sections = sorted(chatbot.works_data["Section"].dropna().unique())
                selected_section = st.sidebar.selectbox("Select a Section", sections)
                if selected_section:
                    section_works_data = chatbot.works_data[
                        chatbot.works_data["Section"] == selected_section
                    ]
                    st.subheader(f"Works for Section: {selected_section}")
                    if view_mode == "Row View":
                        render_work_table(section_works_data)
                    elif view_mode == "Card View":
                        render_work_cards(section_works_data)

    except Exception as e:
        logging.error(f"Error running chatbot app: {e}")
        st.error(f"An error occurred: {e}")


if __name__ == "__main__":
    run_chatbot_app()