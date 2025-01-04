import streamlit as st

def render_station_table(station_data):
    """Render station data in a table view."""
    if station_data.empty:
        st.warning("No station details available.")
    else:
        st.dataframe(station_data)

def render_work_table(work_data):
    """Render works data in a table view."""
    if work_data.empty:
        st.warning("No works found.")
    else:
        st.dataframe(work_data)

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
                <p><b>📝 Remarks:</b> {row.get('Remarks', 'N/A')}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)