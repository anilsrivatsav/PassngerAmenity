# database.py

import sqlite3
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class Database:
    def __init__(self, db_path='railways.db'):
        """
        Initialize the Database object with a path to the SQLite database.
        
        Parameters:
            db_path (str): Path to the SQLite database file.
        """
        self.db_path = db_path
        self.connection = None
        self.connect()
        self.initialize_tables()
    
    def connect(self):
        """Establish a connection to the SQLite database."""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # To access columns by name
            logging.info(f"Connected to SQLite database at {self.db_path}.")
        except sqlite3.Error as e:
            logging.error(f"Error connecting to database: {e}")
            raise
    
    def initialize_tables(self):
        """Create tables if they do not exist."""
        try:
            cursor = self.connection.cursor()
        except Exception as e:
            print(f"An error occurred: {e}")  # Handle the exception
        finally:
            # Enable foreign key support
            cursor.execute("PRAGMA foreign_keys = ON;")
            
            # Table for Stations
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    station_code TEXT UNIQUE NOT NULL,
                    station_name TEXT NOT NULL,
                    categorisation TEXT,
                    zone TEXT,
                    division TEXT,
                    section TEXT,
                    earnings_range TEXT,
                    passenger_range TEXT,
                    passenger_footfall INTEGER,
                    platform_type TEXT,
                    number_of_platforms INTEGER
                );
            """)
            logging.info("Ensured 'stations' table exists.")
            
            # Table for Amenities
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS paavailability (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    station_code TEXT UNIQUE NOT NULL,
                    amenities TEXT,
                    platforms_hl_ml_rl TEXT,
                    number_of_platforms_length_each_pf TEXT,
                    foot_over_bridge TEXT,
                    drinking_water_taps_pf_wise TEXT,
                    seating_arrangement TEXT,
                    platform_shelter_sqm TEXT,
                    urinals TEXT,
                    latrines TEXT,
                    toilet_facility TEXT,
                    number_of_pay_use_toilet_units TEXT,
                    gps_clock TEXT,
                    water_cooler_ro_plant_pf_wise TEXT,
                    dustbins TEXT,
                    announcement_system TEXT,
                    two_wheeler_parking_capacity INTEGER,
                    four_wheeler_parking_capacity INTEGER,
                    pre_paid_taxi_auto_booth TEXT,
                    national_flag TEXT,
                    no_of_daily_trains TEXT,
                    no_of_non_daily_trains TEXT,
                    no_of_functional_uts_counters INTEGER,
                    no_of_functional_prs_counters INTEGER,
                    ladies_sr_citizen_pwd_uts_counter TEXT,
                    no_of_atvm_available INTEGER,
                    no_of_atvm_facilitators INTEGER,
                    enquiry_counter TEXT,
                    current_reservation_facility TEXT,
                    no_of_coaches_longest_stopping_train INTEGER,
                    paid_lounge_ac TEXT,
                    paid_lounge_non_ac TEXT,
                    waiting_hall_ticketing_area TEXT,
                    retiring_room_nos_ac INTEGER,
                    retiring_room_nos_non_ac INTEGER,
                    dormitory_gents_beds INTEGER,
                    dormitory_ladies_beds INTEGER,
                    parcel_office TEXT,
                    no_of_staffs_at_po INTEGER,
                    parcel_packing_available TEXT,
                    reserved_vip_lounge_seating_capacity INTEGER,
                    upper_class_waiting_room_seating_capacity INTEGER,
                    ac_waiting_room_seating_capacity INTEGER,
                    general_waiting_room_seating_capacity INTEGER,
                    ladies_waiting_room_seating_capacity INTEGER,
                    baby_feeding_corner TEXT,
                    medical_emergency_centre TEXT,
                    first_aid_provision TEXT,
                    pharmacy TEXT,
                    battery_operated_cars TEXT,
                    wheel_chair INTEGER,
                    trolley_path TEXT,
                    divyang_toilet TEXT,
                    water_sink_pedestal_for_pwd TEXT,
                    no_of_railway_sahayak INTEGER,
                    no_of_catering_stall_pf_wise INTEGER,
                    no_of_milk_stall_pf_wise INTEGER,
                    no_of_multipurpose_stall_pf_wise INTEGER,
                    ticket_checking_staff_strength INTEGER,
                    osop_stall_location_commodity TEXT,
                    no_of_book_stall_pf_wise INTEGER,
                    ttdc TEXT,
                    hpmc TEXT,
                    food_plaza_irctc TEXT,
                    jana_aahar_irctc TEXT,
                    fast_food_unit_irctc TEXT,
                    refreshment_room_irctc TEXT,
                    vrr_nvrr TEXT,
                    electronic_train_indicator_board TEXT,
                    electronic_coach_indication_board TEXT,
                    rdn_video_wall TEXT,
                    manual_coach_indication_board TEXT,
                    rdn_cctv TEXT,
                    wifi_facility TEXT,
                    lifts_with_location_pf_no TEXT,
                    escalator_with_location_pf_no TEXT,
                    brailee_signage TEXT,
                    atm_facility TEXT,
                    grp_out_post TEXT,
                    rpf_post TEXT,
                    sbi_card_kiosk TEXT,
                    gaming_zone TEXT,
                    cleanliness_of_station TEXT,
                    cloak_room TEXT,
                    subway TEXT,
                    mobile_charging_points TEXT,
                    bottle_crusher TEXT,
                    FOREIGN KEY (station_code) REFERENCES stations(station_code) ON DELETE CASCADE ON UPDATE CASCADE
                );
            """)
            logging.info("Ensured 'paavailability' table exists.")
            
            # Table for Works
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS works (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    works_pending_with TEXT,
                    project_id TEXT UNIQUE NOT NULL,
                    year_of_sanction INTEGER,
                    date_of_sanction TEXT,
                    short_name_of_work TEXT,
                    block_section TEXT,
                    station TEXT,
                    allocation TEXT,
                    cost REAL,
                    expenditure_up_to_date REAL,
                    financial_progress_percent REAL,
                    if_umbrella TEXT,
                    parent_work TEXT,
                    section TEXT,
                    remarks TEXT,
                    latest_remarks_civil TEXT,
                    latest_remarks_electrical TEXT,
                    latest_remarks_s_t TEXT,
                    latest_remarks_civil_as_on TEXT,
                    FOREIGN KEY (works_pending_with) REFERENCES paavailability(station_code) ON DELETE SET NULL ON UPDATE CASCADE
                );
            """)
            logging.info("Ensured 'works' table exists.")
            
            # Table for Remarks
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS remarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    works_pending_with TEXT,
                    project_id TEXT,
                    department TEXT,
                    remark TEXT,
                    FOREIGN KEY (works_pending_with) REFERENCES paavailability(station_code) ON DELETE CASCADE ON UPDATE CASCADE,
                    FOREIGN KEY (project_id) REFERENCES works(project_id) ON DELETE CASCADE ON UPDATE CASCADE
                );
            """)
            logging.info("Ensured 'remarks' table exists.")
            
            self.connection.commit()
            logging.info("Database tables initialized successfully.")

    if __name__ == "__main__":
        # Initialize the database when running this script directly
        db = Database()
   

  