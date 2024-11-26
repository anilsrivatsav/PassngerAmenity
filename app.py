import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
from norms import RailwayAmenities

def load_data():
    try:
        df = pd.read_csv("stations.csv")
        df_amenities = pd.read_csv("paavailability.csv")
        df.columns = df.columns.str.strip()
        df['Categorisation'] = df['Categorisation'].astype(str)
        return df, df_amenities
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None

def format_amenity_value(value):
    if isinstance(value, dict):
        formatted_parts = []
        if 'quantity' in value:
            formatted_parts.append(str(value['quantity']))
        if 'auto_flush' in value and value['auto_flush']:
            formatted_parts.append('Auto Flush')
        if 'note' in value:
            formatted_parts.append(f"({value['note']})")
        if 'required' in value and value['required']:
            if 'with_cover' in value and value['with_cover']:
                formatted_parts.append("With Cover")
            if 'width' in value:
                formatted_parts.append(f"Width: {value['width']}")
        return ' - '.join(formatted_parts)
    return str(value)

def get_numeric_value(value):
    if isinstance(value, dict):
        return int(value.get('quantity', 0))
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

def create_comparison_card(title, required, available):
    req_value = get_numeric_value(required)
    avail_value = get_numeric_value(available)
    
    st.markdown(f"""
    <div class="amenity-card">
        <h5>{title}</h5>
        <p><strong>Required:</strong> {format_amenity_value(required)}</p>
        <p><strong>Available:</strong> {available}</p>
        <p><strong>Status:</strong> {'✅ Compliant' if avail_value >= req_value else f'❌ Shortfall of {req_value - avail_value}'}</p>
    </div>
    """, unsafe_allow_html=True)

def create_station_info_cards(station_data, amenities_data):
    railway_norms = RailwayAmenities()
    
    st.markdown("### 📍 Basic Information")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="info-card">
            <h4>Station Details</h4>
            <p><strong>Code:</strong> {station_data['Station code']}</p>
            <p><strong>Name:</strong> {station_data['STATION NAME']}</p>
            <p><strong>Category:</strong> {station_data['Categorisation']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="info-card">
            <h4>Administrative Info</h4>
            <p><strong>Zone:</strong> {station_data['ZONE']}</p>
            <p><strong>Division:</strong> {station_data['DIVISION']}</p>
            <p><strong>Section:</strong> {station_data['Section']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="info-card">
            <h4>Performance Metrics</h4>
            <p><strong>Earnings Range:</strong> {station_data['Earnings range']}</p>
            <p><strong>Passenger Range:</strong> {station_data['Passenger range']}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 👥 Officials Information")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="info-card">
            <h4>Engineering Department</h4>
            <p><strong>DEN Section:</strong> {station_data['DEN']}</p>
            <p><strong>Sr. DEN:</strong> {station_data['Sr.DEN']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="info-card">
            <h4>Commercial Department</h4>
            <p><strong>CMI:</strong> {station_data['CMI']}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 📋 Station Amenity Requirements")
    category = station_data['Categorisation'].replace('-', '')
    station_amenities = amenities_data[amenities_data['Station_Code'] == station_data['Station code']].iloc[0] if len(amenities_data) > 0 else None
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="card">
            <h4>Minimum Essential Amenities</h4>
        """, unsafe_allow_html=True)
        
        min_amenities = railway_norms.get_minimum_amenities(category)
        if min_amenities and station_amenities is not None:
            for amenity, value in min_amenities.items():
                create_comparison_card(
                    amenity.replace('_', ' ').title(),
                    value,
                    station_amenities.get(f"{amenity}_count", 0)
                )
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <h4>Desirable Amenities</h4>
        """, unsafe_allow_html=True)
        
        desirable_amenities = railway_norms.get_desirable_amenities(category)
        if desirable_amenities and station_amenities is not None:
            for amenity, required in desirable_amenities.items():
                if required:
                    available = bool(station_amenities.get(amenity, False))
                    st.markdown(f"""
                    <div class="amenity-card">
                        <h5>{amenity.replace('_', ' ').title()}</h5>
                        <p><strong>Status:</strong> {'✅ Available' if available else '❌ Not Available'}</p>
                    </div>
                    """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.info("""
    These amenities are based on station categorization norms as per Railway Board guidelines.
    - Minimum Essential Amenities (MEA) are mandatory for the station category
    - Desirable Amenities are recommended based on passenger traffic and station importance
    - Green checkmark (✅) indicates compliance with norms
    - Red cross (❌) indicates shortfall against norms
    """)

def create_app():
    st.set_page_config(layout="wide")
    
    with open('styles.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    st.title('Passenger Amenity Dashboard')
    
    df, df_amenities = load_data()
    if df is None or df_amenities is None:
        return
    
    st.sidebar.header('Station Search')
    search_option = st.sidebar.selectbox('Search by:', ['Station code', 'Categorisation'])
    
    if search_option == 'Station code':
        selected_station = st.sidebar.selectbox('Select Station Code:', ['All'] + sorted(df['Station code'].unique()))
    else:
        selected_station = st.sidebar.selectbox('Select Category:', ['All'] + sorted(df['Categorisation'].unique()))

    if selected_station != 'All':
        if search_option == 'Station code':
            filtered_df = df[df['Station code'] == selected_station]
        else:
            filtered_df = df[df['Categorisation'] == selected_station]
    else:
        filtered_df = df

    tab1, tab2, tab3 = st.tabs(['Overview', 'Analysis', 'Station Details'])
    
    with tab1:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Stations", len(df))
        with col2:
            st.metric("Total Categories", len(df['Categorisation'].unique()))
        with col3:
            st.metric("Total Zones", len(df['ZONE'].unique()))
        with col4:
            st.metric("Total Sections", len(df['Section'].unique()))

        fig1 = px.pie(df, names='Categorisation', title='Distribution by Category', hole=0.4)
        st.plotly_chart(fig1, use_container_width=True)

        zone_counts = df['ZONE'].value_counts().reset_index()
        zone_counts.columns = ['Zone', 'Count']
        fig2 = px.bar(zone_counts, x='Zone', y='Count', title='Stations by Zone')
        st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        section_stats = df.groupby('Section').agg({
            'Station code': 'count',
            'Categorisation': lambda x: x.value_counts().index[0]
        }).reset_index()
        section_stats.columns = ['Section', 'Station Count', 'Most Common Category']
        
        st.subheader('Section-wise Analysis')
        st.dataframe(section_stats)

        cmi_stats = df.groupby('CMI').agg({
            'Station code': 'count',
            'Section': lambda x: ', '.join(x.unique())
        }).reset_index()
        cmi_stats.columns = ['CMI', 'Station Count', 'Sections']
        
        st.subheader('CMI-wise Distribution')
        st.dataframe(cmi_stats)

        earnings_fig = px.histogram(df, x='Earnings range', title='Distribution of Stations by Earnings Range')
        st.plotly_chart(earnings_fig, use_container_width=True)

    with tab3:
        if selected_station != 'All':
            if search_option == 'Station code':
                station_data = filtered_df[filtered_df['Station code'] == selected_station].iloc[0]
                create_station_info_cards(station_data, df_amenities)
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

if __name__ == "__main__":
    create_app()