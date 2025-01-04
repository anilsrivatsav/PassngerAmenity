# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import io
from norms import RailwayAmenities
from database import Database
from works import WorksManager
import datetime
import logging

def load_data(db: Database):
    """
    Load stations and amenities data from the database.
    
    Parameters:
        db (Database): An instance of the Database class.
    
    Returns:
        tuple: DataFrames for stations and amenities.
    """
    try:
        stations_df = pd.read_sql_query("SELECT * FROM stations;", db.connection)
        amenities_df = pd.read_sql_query("SELECT * FROM paavailability;", db.connection)
        return stations_df, amenities_df
    except Exception as e:
        st.error(f"Error loading data from database: {e}")
        return None, None

def create_platform_info_card(platform_info):
    platforms = platform_info.get('platforms_hl_ml_rl', 'N/A')
    platform_count = platform_info.get('number_of_platforms', 'N/A')
    platform_type = platform_info.get('platform_type', 'N/A')

    st.markdown(f"""
    <div class="platform-info-card" style="border: 1px solid #ccc; padding: 10px; border-radius: 5px;">
        <h5>Platform Information</h5>
        <p><strong>Platforms:</strong> {platforms}</p>
        <p><strong>Number of Platforms:</strong> {platform_count}</p>
        <p><strong>Platform Type:</strong> {platform_type}</p>
    </div>
    """, unsafe_allow_html=True)

def create_comparison_card(amenity_name, required_value, available_value):
    # Ensure both required_value and available_value are integers
    required_val = required_value
    if isinstance(required_val, dict):
        # If required_val is a dict, try extracting a numeric key (e.g., 'count')
        required_val = required_val.get('count', 0)

    if not isinstance(required_val, (int, float)):
        required_val = 0

    if not isinstance(available_value, (int, float)):
        # Attempt to convert to int if it's a string
        try:
            available_value = int(available_value)
        except:
            available_value = 0

    status = "✅" if available_value >= required_val else "❌"
    st.markdown(f"""
    <div class="amenity-card" style="border: 1px solid #ddd; padding: 10px; margin-bottom: 10px; border-radius: 5px;">
        <h5>{amenity_name}</h5>
        <p><strong>Required:</strong> {required_val}</p>
        <p><strong>Available:</strong> {available_value}</p>
        <p><strong>Status:</strong> {status}</p>
    </div>
    """, unsafe_allow_html=True)

def create_station_info_cards(station_data, amenities_data, manager: WorksManager):
    railway_norms = RailwayAmenities()

    st.markdown("### 📍 Basic Information")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="info-card" style="border: 1px solid #ccc; padding: 10px; border-radius: 5px;">
            <h4>Station Details</h4>
            <p><strong>Code:</strong> {station_data.get('station_code', 'N/A')}</p>
            <p><strong>Name:</strong> {station_data.get('station_name', 'N/A')}</p>
            <p><strong>Category:</strong> {station_data.get('categorisation', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="info-card" style="border: 1px solid #ccc; padding: 10px; border-radius: 5px;">
            <h4>Administrative Info</h4>
            <p><strong>Zone:</strong> {station_data.get('zone', 'N/A')}</p>
            <p><strong>Division:</strong> {station_data.get('division', 'N/A')}</p>
            <p><strong>Section:</strong> {station_data.get('section', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="info-card" style="border: 1px solid #ccc; padding: 10px; border-radius: 5px;">
            <h4>Performance Metrics</h4>
            <p><strong>Earnings Range:</strong> {station_data.get('earnings_range', 'N/A')}</p>
            <p><strong>Passenger Range:</strong> {station_data.get('passenger_range', 'N/A')}</p>
            <p><strong>Footfall:</strong> {station_data.get('passenger_footfall', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 🛤️ Platform Information")
    create_platform_info_card(station_data)

    st.markdown("### 👥 Officials Information")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="info-card" style="border: 1px solid #ccc; padding: 10px; border-radius: 5px;">
            <h4>Engineering Department</h4>
            <p><strong>DEN Section:</strong> {station_data.get('den', 'N/A')}</p>
            <p><strong>Sr. DEN:</strong> {station_data.get('sr_den', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="info-card" style="border: 1px solid #ccc; padding: 10px; border-radius: 5px;">
            <h4>Commercial Department</h4>
            <p><strong>CMI:</strong> {station_data.get('cmi', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 📋 Station Amenity Requirements")
    category = station_data.get('categorisation', 'N/A').replace('-', '')

    # Match station code from stations table with station_code in paavailability table
    station_code = station_data.get('station_code', '').strip()
    if 'station_code' not in amenities_data.columns:
        st.error("'station_code' column not found in paavailability table. Please verify column names.")
        station_amenities = None
    else:
        station_amenities = amenities_data[amenities_data['station_code'].str.strip() == station_code]
        station_amenities = station_amenities.iloc[0].to_dict() if not station_amenities.empty else None

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="card" style="border: 1px solid #ccc; padding: 10px; border-radius: 5px;">
            <h4>Minimum Essential Amenities</h4>
        """, unsafe_allow_html=True)
        
        min_amenities = railway_norms.get_minimum_amenities(category)
        if min_amenities and station_amenities is not None:
            for amenity, value in min_amenities.items():
                # Assuming available_value is stored as 'amenity_count' in paavailability
                available_value = station_amenities.get(f"{amenity}_count", 0)
                create_comparison_card(
                    amenity.replace('_', ' ').title(),
                    value,
                    available_value
                )
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card" style="border: 1px solid #ccc; padding: 10px; border-radius: 5px;">
            <h4>Desirable Amenities</h4>
        """, unsafe_allow_html=True)
        
        desirable_amenities = railway_norms.get_desirable_amenities(category)
        if desirable_amenities and station_amenities is not None:
            for amenity, required in desirable_amenities.items():
                if required:
                    available = bool(station_amenities.get(amenity, False))
                    st.markdown(f"""
                    <div class="amenity-card" style="border: 1px solid #ddd; padding: 10px; margin-bottom: 10px; border-radius: 5px;">
                        <h5>{amenity.replace('_', ' ').title()}</h5>
                        <p><strong>Status:</strong> {'✅ Available' if available else '❌ Not Available'}</p>
                    </div>
                    """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Display related works
    st.markdown("### 📑 Related Works")
    try:
        works_df = pd.read_sql_query("""
            SELECT * FROM works WHERE works_pending_with = ?;
        """, self.db.connection, params=(station_code,))
        if not works_df.empty:
            st.dataframe(works_df)
        else:
            st.write("No related works found for this station.")
    except Exception as e:
        st.error(f"Error fetching related works: {e}")

def create_app():
    st.set_page_config(layout="wide")
    st.title('Passenger Amenity Dashboard')

    # Initialize the database and manager
    db = Database()
    manager = WorksManager(db)

    # Initialize data from CSVs if database tables are empty
    def check_and_initialize():
        stations_count = pd.read_sql_query("SELECT COUNT(*) as count FROM stations;", db.connection)['count'][0]
        if stations_count == 0:
            st.info("Initializing database with data from CSV files...")
            manager.initialize_data_from_csv(csv_folder='.')
            st.success("Database initialized successfully!")
        else:
            logging.info("Database already initialized. Skipping data initialization.")

    check_and_initialize()

    # Load data from the database
    stations_df, amenities_df = load_data(db)
    if stations_df is None or amenities_df is None:
        return

    # Sidebar navigation for Dashboard or Works
    page = st.sidebar.radio("Navigation", ["Dashboard", "Works"])

    if page == "Dashboard":
        st.sidebar.header('Station Search')
        search_option = st.sidebar.selectbox('Search by:', ['Station code', 'Categorisation'])
        
        if search_option == 'Station code':
            selected_station = st.sidebar.selectbox('Select Station Code:', ['All'] + sorted(stations_df['station_code'].unique()))
            if selected_station != 'All':
                filtered_df = stations_df[stations_df['station_code'] == selected_station]
            else:
                filtered_df = stations_df
        else:
            selected_category = st.sidebar.selectbox('Select Category:', ['All'] + sorted(stations_df['categorisation'].unique()))
            if selected_category != 'All':
                filtered_df = stations_df[stations_df['categorisation'] == selected_category]
            else:
                filtered_df = stations_df

        tab1, tab2, tab3 = st.tabs(['Overview', 'Analysis', 'Station Details'])
        
        with tab1:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Stations", len(stations_df))
            with col2:
                st.metric("Total Categories", len(stations_df['categorisation'].unique()))
            with col3:
                st.metric("Total Zones", len(stations_df['zone'].unique()))
            with col4:
                st.metric("Total Sections", len(stations_df['section'].unique()))

            fig1 = px.pie(stations_df, names='categorisation', title='Distribution by Category', hole=0.4)
            st.plotly_chart(fig1, use_container_width=True)

            zone_counts = stations_df['zone'].value_counts().reset_index()
            zone_counts.columns = ['Zone', 'Count']
            fig2 = px.bar(zone_counts, x='Zone', y='Count', title='Stations by Zone')
            st.plotly_chart(fig2, use_container_width=True)

        with tab2:
            # Section-wise Analysis
            section_stats = stations_df.groupby('section').agg({
                'station_code': 'count',
                'categorisation': lambda x: x.value_counts().index[0] if not x.value_counts().empty else 'N/A'
            }).reset_index()
            section_stats.columns = ['Section', 'Station Count', 'Most Common Category']
            
            st.subheader('Section-wise Analysis')
            st.dataframe(section_stats)

            earnings_fig = px.histogram(stations_df, x='earnings_range', title='Distribution of Stations by Earnings Range')
            st.plotly_chart(earnings_fig, use_container_width=True)

        with tab3:
            if search_option == 'Station code' and selected_station != 'All':
                # Show detailed info for the selected station
                station_data = filtered_df.iloc[0].to_dict()
                create_station_info_cards(station_data, amenities_df, manager)
                st.markdown("---")
            
            st.subheader('Station List')
            st.dataframe(filtered_df)
            
            col1, col2 = st.columns(2)
            with col1:
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    csv,
                    "station_data.csv",
                    "text/csv"
                )
            with col2:
                excel_buffer = io.BytesIO()
                filtered_df.to_excel(excel_buffer, index=False)
                st.download_button(
                    "Download Excel",
                    excel_buffer.getvalue(),
                    "station_data.xlsx",
                    "application/vnd.ms-excel"
                )
    
    elif page == "Works":
        st.header("PH-53 Works Management")

        # Tabs within Works section
        wtab1, wtab2, wtab3 = st.tabs(["Summary", "Remarks", "Manage Works"])

        with wtab1:
            st.subheader("Summary of Sanctioned PH-53 Works")
            summary_df = manager.summarize_ph53_works()
            st.dataframe(summary_df)

            # Optionally, add charts
            fig = px.bar(summary_df[summary_df["works_pending_with"] != "Total Works"],
                         x="works_pending_with",
                         y="total_pids_sanctioned",
                         title="Total PIDs by Pending Authority")
            st.plotly_chart(fig, use_container_width=True)

        with wtab2:
            st.subheader("Remarks with Dates")
            remarks_df = manager.get_all_remarks()
            st.dataframe(remarks_df)

            # Optional filtering by department
            if not remarks_df.empty:
                selected_dept = st.selectbox("Filter by Department:", ["All"] + sorted(remarks_df['department'].unique()))
                if selected_dept != "All":
                    filtered_remarks = remarks_df[remarks_df['department'] == selected_dept]
                else:
                    filtered_remarks = remarks_df
                st.dataframe(filtered_remarks)

            # Download button for remarks
            if not filtered_remarks.empty:
                csv_remarks = filtered_remarks.to_csv(index=False)
                st.download_button("Download Remarks CSV", csv_remarks, "remarks.csv", "text/csv")

        with wtab3:
            st.subheader("Manage Works")
            action = st.selectbox("Select Action", ["Add New Work", "Edit Existing Work"])

            if action == "Add New Work":
                st.markdown("### Add a New Work Record")
                with st.form("add_work_form"):
                    works_pending_with = st.selectbox("Works Pending With", sorted(amenities_df['station_code'].unique()))
                    project_id = st.text_input("Project ID")
                    year_of_sanction = st.number_input("Year of Sanction", min_value=1900, max_value=2100, step=1)
                    date_of_sanction = st.date_input("Date of Sanction", value=datetime.date.today())
                    short_name_of_work = st.text_input("Short Name of Work")
                    block_section = st.text_input("Block Section")
                    station = st.text_input("Station")
                    allocation = st.text_input("Allocation")
                    cost = st.number_input("Cost", min_value=0.0, step=100.0)
                    expenditure_up_to_date = st.number_input("Expenditure Up To Date", min_value=0.0, step=100.0)
                    financial_progress_percent = st.number_input("Financial Progress (%)", min_value=0.0, max_value=100.0, step=1.0)
                    if_umbrella = st.selectbox("If Umbrella?", ["Yes", "No"])
                    parent_work = st.text_input("Parent Work")
                    section = st.text_input("Section")
                    remarks = st.text_area("Remarks")
                    latest_remarks_civil = st.text_area("Latest Remarks Civil")
                    latest_remarks_electrical = st.text_area("Latest Remarks Electrical")
                    latest_remarks_s_t = st.text_area("Latest Remarks S&T")
                    latest_remarks_civil_as_on = st.text_input("Latest Remarks Civil As On (DD-MM-YYYY)")
                    
                    submitted = st.form_submit_button("Add Work")
                    if submitted:
                        if not project_id:
                            st.error("Project ID is required.")
                        else:
                            work_data = {
                                "works_pending_with": works_pending_with,
                                "project_id": project_id,
                                "year_of_sanction": year_of_sanction,
                                "date_of_sanction": date_of_sanction.strftime("%d-%m-%Y"),
                                "short_name_of_work": short_name_of_work,
                                "block_section": block_section,
                                "station": station,
                                "allocation": allocation,
                                "cost": cost,
                                "expenditure_up_to_date": expenditure_up_to_date,
                                "financial_progress_percent": financial_progress_percent,
                                "if_umbrella": if_umbrella,
                                "parent_work": parent_work,
                                "section": section,
                                "remarks": remarks,
                                "latest_remarks_civil": latest_remarks_civil,
                                "latest_remarks_electrical": latest_remarks_electrical,
                                "latest_remarks_s_t": latest_remarks_s_t,
                                "latest_remarks_civil_as_on": latest_remarks_civil_as_on
                            }
                            success = manager.add_work_record(work_data)
                            if success:
                                st.success("Work record added successfully!")
                            else:
                                st.error("Failed to add work record. Check logs for details.")

            elif action == "Edit Existing Work":
                st.markdown("### Edit an Existing Work Record")
                works_df = manager.get_all_works()
                if works_df.empty:
                    st.info("No work records available to edit.")
                else:
                    project_ids = sorted(works_df['project_id'].unique())
                    selected_project_id = st.selectbox("Select Project ID to Edit", project_ids)
                    if selected_project_id:
                        work = manager.get_work_by_id(selected_project_id)
                        if work:
                            with st.form("edit_work_form"):
                                # Pre-fill the form with existing data
                                works_pending_with = st.selectbox(
                                    "Works Pending With", 
                                    sorted(amenities_df['station_code'].unique()), 
                                    index=sorted(amenities_df['station_code'].unique()).index(work['works_pending_with']) if work['works_pending_with'] in sorted(amenities_df['station_code'].unique()) else 0
                                )
                                year_of_sanction = st.number_input(
                                    "Year of Sanction", 
                                    min_value=1900, max_value=2100, step=1, 
                                    value=work['year_of_sanction']
                                )
                                date_of_sanction = st.date_input(
                                    "Date of Sanction", 
                                    value=datetime.datetime.strptime(work['date_of_sanction'], "%d-%m-%Y").date()
                                )
                                short_name_of_work = st.text_input(
                                    "Short Name of Work", 
                                    value=work['short_name_of_work']
                                )
                                block_section = st.text_input(
                                    "Block Section", 
                                    value=work['block_section']
                                )
                                station = st.text_input(
                                    "Station", 
                                    value=work['station']
                                )
                                allocation = st.text_input(
                                    "Allocation", 
                                    value=work['allocation']
                                )
                                cost = st.number_input(
                                    "Cost", 
                                    min_value=0.0, step=100.0, 
                                    value=work['cost']
                                )
                                expenditure_up_to_date = st.number_input(
                                    "Expenditure Up To Date", 
                                    min_value=0.0, step=100.0, 
                                    value=work['expenditure_up_to_date']
                                )
                                financial_progress_percent = st.number_input(
                                    "Financial Progress (%)", 
                                    min_value=0.0, max_value=100.0, step=1.0, 
                                    value=work['financial_progress_percent']
                                )
                                if_umbrella = st.selectbox(
                                    "If Umbrella?", 
                                    ["Yes", "No"], 
                                    index=0 if work['if_umbrella'].lower() == 'yes' else 1
                                )
                                parent_work = st.text_input(
                                    "Parent Work", 
                                    value=work['parent_work']
                                )
                                section = st.text_input(
                                    "Section", 
                                    value=work['section']
                                )
                                remarks = st.text_area(
                                    "Remarks", 
                                    value=work['remarks']
                                )
                                latest_remarks_civil = st.text_area(
                                    "Latest Remarks Civil", 
                                    value=work['latest_remarks_civil']
                                )
                                latest_remarks_electrical = st.text_area(
                                    "Latest Remarks Electrical", 
                                    value=work['latest_remarks_electrical']
                                )
                                latest_remarks_s_t = st.text_area(
                                    "Latest Remarks S&T", 
                                    value=work['latest_remarks_s_t']
                                )
                                latest_remarks_civil_as_on = st.text_input(
                                    "Latest Remarks Civil As On (DD-MM-YYYY)", 
                                    value=work['latest_remarks_civil_as_on']
                                )
                                
                                submitted = st.form_submit_button("Update Work")
                                if submitted:
                                    updated_data = {
                                        "works_pending_with": works_pending_with,
                                        "year_of_sanction": year_of_sanction,
                                        "date_of_sanction": date_of_sanction.strftime("%d-%m-%Y"),
                                        "short_name_of_work": short_name_of_work,
                                        "block_section": block_section,
                                        "station": station,
                                        "allocation": allocation,
                                        "cost": cost,
                                        "expenditure_up_to_date": expenditure_up_to_date,
                                        "financial_progress_percent": financial_progress_percent,
                                        "if_umbrella": if_umbrella,
                                        "parent_work": parent_work,
                                        "section": section,
                                        "remarks": remarks,
                                        "latest_remarks_civil": latest_remarks_civil,
                                        "latest_remarks_electrical": latest_remarks_electrical,
                                        "latest_remarks_s_t": latest_remarks_s_t,
                                        "latest_remarks_civil_as_on": latest_remarks_civil_as_on
                                    }
                                    success = manager.edit_work_record(selected_project_id, updated_data)
                                    if success:
                                        st.success("Work record updated successfully!")
                                    else:
                                        st.error("Failed to update work record. Check logs for details.")
                        else:
                            st.error("Selected work record not found.")

    if __name__ == "__main__":
        create_app()
