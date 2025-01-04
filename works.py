
# works.py

import sqlite3
import logging
from database import Database
import pandas as pd
import datetime
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class WorksManager:
    """
    A class to manage PH-53 works data, including CRUD operations and remarks handling.
    """
    
    def __init__(self, db: Database):
        """
        Initialize the WorksManager with a Database object.
        
        Parameters:
            db (Database): An instance of the Database class for DB operations.
        """
        self.db = db
        self.conn = self.db.connection
        logging.info("WorksManager initialized.")
    
    def add_work_record(self, work_data: dict):
        """
        Add a new work record to the 'works' table.
        
        Parameters:
            work_data (dict): A dictionary containing work details.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO works (
                    works_pending_with,
                    project_id,
                    year_of_sanction,
                    date_of_sanction,
                    short_name_of_work,
                    block_section,
                    station,
                    allocation,
                    cost,
                    expenditure_up_to_date,
                    financial_progress_percent,
                    if_umbrella,
                    parent_work,
                    section,
                    remarks,
                    latest_remarks_civil,
                    latest_remarks_electrical,
                    latest_remarks_s_t,
                    latest_remarks_civil_as_on
                ) VALUES (
                    :works_pending_with,
                    :project_id,
                    :year_of_sanction,
                    :date_of_sanction,
                    :short_name_of_work,
                    :block_section,
                    :station,
                    :allocation,
                    :cost,
                    :expenditure_up_to_date,
                    :financial_progress_percent,
                    :if_umbrella,
                    :parent_work,
                    :section,
                    :remarks,
                    :latest_remarks_civil,
                    :latest_remarks_electrical,
                    :latest_remarks_s_t,
                    :latest_remarks_civil_as_on
                );
            """, work_data)
            self.conn.commit()
            logging.info(f"Added new work record: {work_data.get('project_id')}")
            return True
        except sqlite3.IntegrityError as e:
            logging.error(f"IntegrityError while adding work record: {e}")
            return False
        except Exception as e:
            logging.error(f"Error while adding work record: {e}")
            return False
    
    def edit_work_record(self, project_id: str, updated_data: dict):
        """
        Edit an existing work record in the 'works' table.
        
        Parameters:
            project_id (str): The PROJECTID of the work to update.
            updated_data (dict): A dictionary containing updated work details.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        try:
            cursor = self.conn.cursor()
            # Prepare the SET part of the SQL statement
            set_clause = ", ".join([f"{key} = :{key}" for key in updated_data.keys()])
            updated_data['project_id'] = project_id
            sql = f"UPDATE works SET {set_clause} WHERE project_id = :project_id;"
            cursor.execute(sql, updated_data)
            if cursor.rowcount == 0:
                logging.warning(f"No work record found with PROJECTID: {project_id}")
                return False
            self.conn.commit()
            logging.info(f"Edited work record: {project_id}")
            return True
        except Exception as e:
            logging.error(f"Error while editing work record: {e}")
            return False
    
    def get_all_works(self) -> pd.DataFrame:
        """
        Retrieve all work records from the 'works' table.
        
        Returns:
            pd.DataFrame: DataFrame containing all works.
        """
        try:
            df = pd.read_sql_query("SELECT * FROM works;", self.conn)
            logging.info("Fetched all work records.")
            return df
        except Exception as e:
            logging.error(f"Error fetching work records: {e}")
            return pd.DataFrame()
    
    def get_work_by_id(self, project_id: str) -> dict:
        """
        Retrieve a single work record by PROJECTID.
        
        Parameters:
            project_id (str): The PROJECTID of the work.
        
        Returns:
            dict: Dictionary containing the work details, or empty dict if not found.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM works WHERE project_id = ?;", (project_id,))
            row = cursor.fetchone()
            if row:
                work = dict(row)
                logging.info(f"Fetched work record: {project_id}")
                return work
            else:
                logging.warning(f"No work record found with PROJECTID: {project_id}")
                return {}
        except Exception as e:
            logging.error(f"Error fetching work record by PROJECTID: {e}")
            return {}
    
    def add_remark(self, remark_data: dict):
        """
        Add a new remark to the 'remarks' table.
        
        Parameters:
            remark_data (dict): A dictionary containing remark details.
        
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO remarks (
                    date,
                    works_pending_with,
                    project_id,
                    department,
                    remark
                ) VALUES (
                    :date,
                    :works_pending_with,
                    :project_id,
                    :department,
                    :remark
                );
            """, remark_data)
            self.conn.commit()
            logging.info(f"Added new remark for PROJECTID: {remark_data.get('project_id')}")
            return True
        except Exception as e:
            logging.error(f"Error while adding remark: {e}")
            return False
    
    def get_all_remarks(self) -> pd.DataFrame:
        """
        Retrieve all remarks from the 'remarks' table.
        
        Returns:
            pd.DataFrame: DataFrame containing all remarks.
        """
        try:
            df = pd.read_sql_query("SELECT * FROM remarks ORDER BY date DESC;", self.conn)
            logging.info("Fetched all remarks.")
            return df
        except Exception as e:
            logging.error(f"Error fetching remarks: {e}")
            return pd.DataFrame()
    
    def summarize_ph53_works(self) -> pd.DataFrame:
        """
        Summarize PH-53 works by categorizing them based on their 'Status'.
        Assumes that 'Status' is part of the 'works' table or needs to be determined.
        Adjust the logic based on actual data schema.
    
        Returns:
            pd.DataFrame: A summary DataFrame containing aggregated counts for each "Works Pending with".
        """
        try:
            query = """
                SELECT 
                    works_pending_with,
                    COUNT(*) AS total_pids_sanctioned,
                    SUM(CASE WHEN financial_progress_percent >= 100 THEN 1 ELSE 0 END) AS works_completed_pending_cr_fcc_bill,
                    SUM(CASE WHEN financial_progress_percent < 100 AND financial_progress_percent >= 50 THEN 1 ELSE 0 END) AS tender_to_be_called,
                    SUM(CASE WHEN financial_progress_percent < 50 AND financial_progress_percent >= 25 THEN 1 ELSE 0 END) AS tender_under_finalization_loa_issued,
                    SUM(CASE WHEN financial_progress_percent < 25 THEN 1 ELSE 0 END) AS work_in_progress
                FROM works
                GROUP BY works_pending_with
            """
            df = pd.read_sql_query(query, self.conn)
            
            # Adding Total Row
            total_row = {
                "works_pending_with": "Total Works",
                "total_pids_sanctioned": df["total_pids_sanctioned"].sum(),
                "works_completed_pending_cr_fcc_bill": df["works_completed_pending_cr_fcc_bill"].sum(),
                "tender_to_be_called": df["tender_to_be_called"].sum(),
                "tender_under_finalization_loa_issued": df["tender_under_finalization_loa_issued"].sum(),
                "work_in_progress": df["work_in_progress"].sum()
            }
            df = df.append(total_row, ignore_index=True)
            
            logging.info("PH-53 works summary created successfully.")
            return df
        except Exception as e:
            logging.error(f"Error summarizing PH-53 works: {e}")
            return pd.DataFrame()
    
    def get_remarks_with_dates(self) -> pd.DataFrame:
        """
        Collect remarks from all data sets with the current date attached.
        Remarks columns may vary; any column containing 'Remarks' or 'Latest Remarks' is considered.
        
        Returns:
            pd.DataFrame: A DataFrame with columns 
            ['Date', 'Works Pending with', 'PROJECTID', 'Department', 'Remark'].
        """
        try:
            df = self.get_all_remarks()
            if df.empty:
                logging.info("No remarks data found.")
                return df
            return df
        except Exception as e:
            logging.error(f"Error collecting remarks with dates: {e}")
            return pd.DataFrame()
    
    def initialize_data_from_csv(self, csv_folder: str = '.'):
        """
        Initialize the database with data from CSV files located in the specified folder.
        It detects and imports data for stations, paavailability, works, and remarks.
        
        Parameters:
            csv_folder (str): Path to the folder containing CSV files.
                              Defaults to the current directory.
        """
        try:
            # Initialize stations from 'stations.csv'
            stations_csv = os.path.join(csv_folder, 'stations.csv')
            with open(stations_csv, 'r') as file:
                data = file.read()  # Dummy read operation
        except FileNotFoundError:
            print(f"Error: The file '{stations_csv}' was not found.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        finally:
            if os.path.isfile(stations_csv):
                stations_df = pd.read_csv(stations_csv)
                for _, row in stations_df.iterrows():
                    station_data = {
                        "station_code": row.get('Station code', '').strip(),
                        "station_name": row.get('STATION NAME', '').strip(),
                        "categorisation": row.get('Categorisation', '').strip(),
                        "zone": row.get('ZONE', '').strip(),
                        "division": row.get('DIVISION', '').strip(),
                        "section": row.get('Section', '').strip(),
                        "earnings_range": row.get('Earnings range', '').strip(),
                        "passenger_range": row.get('Passenger range', '').strip(),
                        "passenger_footfall": int(row.get('Passenger footfall', 0)),
                        "platform_type": row.get('Platform Type', 'Unknown').strip(),
                        "number_of_platforms": int(row.get('Number of Platforms', 0))
                    }
                    try:
                        self.conn.execute("""
                            INSERT OR IGNORE INTO stations (
                                station_code, station_name, categorisation, zone, division, section, 
                                earnings_range, passenger_range, passenger_footfall, platform_type, number_of_platforms
                            ) VALUES (
                                :station_code, :station_name, :categorisation, :zone, :division, :section, 
                                :earnings_range, :passenger_range, :passenger_footfall, :platform_type, :number_of_platforms
                            );
                        """, station_data)
                        logging.info(f"Inserted/Skipped station: {station_data['station_code']}")
                    except Exception as e:
                        logging.error(f"Error inserting station {station_data['station_code']}: {e}")
                self.conn.commit()
                logging.info("Stations data initialized from CSV.")
            else:
                logging.warning(f"'stations.csv' not found in {csv_folder}. Skipping stations initialization.")
            
            # Initialize paavailability from 'paavailability.csv'
            paavailability_csv = os.path.join(csv_folder, 'paavailability.csv')
            if os.path.isfile(paavailability_csv):
                pa_df = pd.read_csv(paavailability_csv)
                for _, row in pa_df.iterrows():
                    pa_data = {
                        "station_code": row.get('Stations ', '').strip(),
                        "amenities": row.get('Amenities', '').strip(),
                        "platforms_hl_ml_rl": row.get('Platforms -HL/ML/RL', '').strip(),
                        "number_of_platforms_length_each_pf": row.get('No. of Platforms (Length of Each PF)', '').strip(),
                        "foot_over_bridge": row.get('Foot over bridge (with Ramp or Steps)', '').strip(),
                        "drinking_water_taps_pf_wise": row.get('Drinking water taps (PF wise)', '').strip(),
                        "seating_arrangement": row.get('Seating Arrangement (no. of passenger/PF)', '').strip(),
                        "platform_shelter_sqm": row.get('Platform Shelter ((PF wise: in sqm)', '').strip(),
                        "urinals": row.get("Urinals (including W/R's & Pay & Use Toilet)", '').strip(),
                        "latrines": row.get('Latrines', '').strip(),
                        "toilet_facility": row.get('Toilet Facility/Pay & Use toilet in Circulating area', '').strip(),
                        "number_of_pay_use_toilet_units": row.get('No. of Pay & Use toilet units (Platform wise)', '').strip(),
                        "gps_clock": row.get('GPS Clock', '').strip(),
                        "water_cooler_ro_plant_pf_wise": row.get('Water Cooler/RO Palnt PF wise', '').strip(),
                        "dustbins": row.get('Dustbins (Dry & Wet In Pairs)', '').strip(),
                        "announcement_system": row.get('Announcement System (Computerised/Manual)', '').strip(),
                        "two_wheeler_parking_capacity": int(row.get('2 Wheeler Parking (Capacity)', 0)),
                        "four_wheeler_parking_capacity": int(row.get('4 Wheeler Parking (Capacity)', 0)),
                        "pre_paid_taxi_auto_booth": row.get('Pre Paid Taxi/Auto Booth', '').strip(),
                        "national_flag": row.get('100ft tall National flag in Circulating area', '').strip(),
                        "no_of_daily_trains": row.get('No. of Daily Trains (Ordinary & Express) (---- / ----)', '').strip(),
                        "no_of_non_daily_trains": row.get('No. of non-daily Trains (Ordinary & Express) (---- / ----)', '').strip(),
                        "no_of_functional_uts_counters": int(row.get('No. of functional UTS Counters', 0)),
                        "no_of_functional_prs_counters": int(row.get('No. of functional PRS Counters', 0)),
                        "ladies_sr_citizen_pwd_uts_counter": row.get('Ladies/Sr.Citizen/PWD (Divyangjan) UTS Counter (Yes/No)', '').strip(),
                        "no_of_atvm_available": int(row.get('No. of ATVM available', 0)),
                        "no_of_atvm_facilitators": int(row.get('No. of ATVM Facilitators', 0)),
                        "enquiry_counter": row.get('Enquiry Counter (Yes/No)', '').strip(),
                        "current_reservation_facility": row.get('Current Reservation Facility (Yes/No)', '').strip(),
                        "no_of_coaches_longest_stopping_train": int(row.get('No. of Coaches of Longest stopping train', 0)),
                        "paid_lounge_ac": row.get('Paid Lounge (A/C)', '').strip(),
                        "paid_lounge_non_ac": row.get('Paid Lounge (Non-A/C)', '').strip(),
                        "waiting_hall_ticketing_area": row.get('Waiting Hall/Ticketing area', '').strip(),
                        "retiring_room_nos_ac": int(row.get('Retiring Room Nos. (AC)', 0)),
                        "retiring_room_nos_non_ac": int(row.get('Retiring Room Nos. (Non AC)', 0)),
                        "dormitory_gents_beds": int(row.get('Dormitoty for Gents (No. of Beds)', 0)),
                        "dormitory_ladies_beds": int(row.get('Dormitoty for Ladies (No. of Beds)', 0)),
                        "parcel_office": row.get('Parcel Office (Yes/No)', '').strip(),
                        "no_of_staffs_at_po": int(row.get('No. of Staffs at PO', 0)),
                        "parcel_packing_available": row.get('Parcel Packing: Available or not', '').strip(),
                        "reserved_vip_lounge_seating_capacity": int(row.get('Reserved/VIP Lounge (Seating Capacity)', 0)),
                        "upper_class_waiting_room_seating_capacity": int(row.get('Upper Class Waiting Room (Seating Capacity)', 0)),
                        "ac_waiting_room_seating_capacity": int(row.get('AC Waiting Room (Seating Capacity)', 0)),
                        "general_waiting_room_seating_capacity": int(row.get('General Waiting Room (Seating Capacity)', 0)),
                        "ladies_waiting_room_seating_capacity": int(row.get('Ladies Waiting Room (Seating Capacity)', 0)),
                        "baby_feeding_corner": row.get('Baby feeding Corner (Yes/No)', '').strip(),
                        "medical_emergency_centre": row.get('Free Medical Emergency Centre / Ambulance: Name of Hospital backed by', '').strip(),
                        "first_aid_provision": row.get('First Aid Provision', '').strip(),
                        "pharmacy": row.get('Pharmacy', '').strip(),
                        "battery_operated_cars": row.get('Battery Operated Cars (Nos. & Tariff per Passenger)', '').strip(),
                        "wheel_chair": int(row.get('Wheel Chair (Nos.)', 0)),
                        "trolley_path": row.get('Trolley Path (Available at 1 end or Both Or not available)', '').strip(),
                        "divyang_toilet": row.get('Divyang Toilet', '').strip(),
                        "water_sink_pedestal_for_pwd": row.get('Water sink/pedestal for PWD (Divyangjan) (atleast 1 unit)', '').strip(),
                        "no_of_railway_sahayak": int(row.get('No. of Railway Sahayak (Licensed porters)', 0)),
                        "no_of_catering_stall_pf_wise": int(row.get('No. of Catering stall (PF Wise)', 0)),
                        "no_of_milk_stall_pf_wise": int(row.get('No. of Milk stall (PF Wise)', 0)),
                        "no_of_multipurpose_stall_pf_wise": int(row.get('No. of Multipurpose stall (PF Wise)', 0)),
                        "ticket_checking_staff_strength": int(row.get('Ticket Checking staffs strength', 0)),
                        "osop_stall_location_commodity": row.get('OSOP stall (Location & Commodity)', '').strip(),
                        "no_of_book_stall_pf_wise": int(row.get('No. of Book stall (PF Wise)', 0)),
                        "ttdc": row.get('TTDC', '').strip(),
                        "hpmc": row.get('HPMC', '').strip(),
                        "food_plaza_irctc": row.get('Food Plaza (IRCTC)', '').strip(),
                        "jana_aahar_irctc": row.get('Jana Aahar (IRCTC)', '').strip(),
                        "fast_food_unit_irctc": row.get('Fast Food Unit (IRCTC)', '').strip(),
                        "refreshment_room_irctc": row.get('Refreshment Room (IRCTC)', '').strip(),
                        "vrr_nvrr": row.get('VRR/NVRR', '').strip(),
                        "electronic_train_indicator_board": row.get('Electronic Train indicator Board', '').strip(),
                        "electronic_coach_indication_board": row.get('Electronic Coach Indication Board', '').strip(),
                        "rdn_video_wall": row.get('RDN Video Wall (Nos. with Location)', '').strip(),
                        "manual_coach_indication_board": row.get('Manual Coach Indication Board', '').strip(),
                        "rdn_cctv": row.get('RDN CCTV (Train Arr./Dep.)', '').strip(),
                        "wifi_facility": row.get('Wi-Fi Facility (Yes/No)', '').strip(),
                        "lifts_with_location_pf_no": row.get('Lifts with Location/PF No.', '').strip(),
                        "escalator_with_location_pf_no": row.get('Escalator with Location/PF No.', '').strip(),
                        "brailee_signage": row.get('Brailee Signage (Station Map & Plates)', '').strip(),
                        "atm_facility": row.get('ATM Facility', '').strip(),
                        "grp_out_post": row.get('GRP out post', '').strip(),
                        "rpf_post": row.get('RPF post', '').strip(),
                        "sbi_card_kiosk": row.get('SBI Card KIOSK', '').strip(),
                        "gaming_zone": row.get('Gaming Zone', '').strip(),
                        "cleanliness_of_station": row.get('Cleanliness of Station (DEnHM or Station Imprest)', '').strip(),
                        "cloak_room": row.get('Cloak Room', '').strip(),
                        "subway": row.get('Subway', '').strip(),
                        "mobile_charging_points": row.get('Mobile charging points', '').strip(),
                        "bottle_crusher": row.get('Bottle Crusher', '').strip()
                    }
                    try:
                        self.conn.execute("""
                            INSERT OR IGNORE INTO paavailability (
                                station_code, amenities, platforms_hl_ml_rl, number_of_platforms_length_each_pf,
                                foot_over_bridge, drinking_water_taps_pf_wise, seating_arrangement, platform_shelter_sqm,
                                urinals, latrines, toilet_facility, number_of_pay_use_toilet_units, gps_clock,
                                water_cooler_ro_plant_pf_wise, dustbins, announcement_system, two_wheeler_parking_capacity,
                                four_wheeler_parking_capacity, pre_paid_taxi_auto_booth, national_flag, no_of_daily_trains,
                                no_of_non_daily_trains, no_of_functional_uts_counters, no_of_functional_prs_counters,
                                ladies_sr_citizen_pwd_uts_counter, no_of_atvm_available, no_of_atvm_facilitators,
                                enquiry_counter, current_reservation_facility, no_of_coaches_longest_stopping_train,
                                paid_lounge_ac, paid_lounge_non_ac, waiting_hall_ticketing_area, retiring_room_nos_ac,
                                retiring_room_nos_non_ac, dormitory_gents_beds, dormitory_ladies_beds, parcel_office,
                                no_of_staffs_at_po, parcel_packing_available, reserved_vip_lounge_seating_capacity,
                                upper_class_waiting_room_seating_capacity, ac_waiting_room_seating_capacity,
                                general_waiting_room_seating_capacity, ladies_waiting_room_seating_capacity,
                                baby_feeding_corner, medical_emergency_centre, first_aid_provision, pharmacy,
                                battery_operated_cars, wheel_chair, trolley_path, divyang_toilet,
                                water_sink_pedestal_for_pwd, no_of_railway_sahayak, no_of_catering_stall_pf_wise,
                                no_of_milk_stall_pf_wise, no_of_multipurpose_stall_pf_wise, ticket_checking_staff_strength,
                                osop_stall_location_commodity, no_of_book_stall_pf_wise, ttdc, hpmc,
                                food_plaza_irctc, jana_aahar_irctc, fast_food_unit_irctc, refreshment_room_irctc,
                                vrr_nvrr, electronic_train_indicator_board, electronic_coach_indication_board,
                                rdn_video_wall, manual_coach_indication_board, rdn_cctv, wifi_facility,
                                lifts_with_location_pf_no, escalator_with_location_pf_no, brailee_signage,
                                atm_facility, grp_out_post, rpf_post, sbi_card_kiosk, gaming_zone,
                                cleanliness_of_station, cloak_room, subway, mobile_charging_points, bottle_crusher
                            ) VALUES (
                                :station_code, :amenities, :platforms_hl_ml_rl, :number_of_platforms_length_each_pf,
                                :foot_over_bridge, :drinking_water_taps_pf_wise, :seating_arrangement, :platform_shelter_sqm,
                                :urinals, :latrines, :toilet_facility, :number_of_pay_use_toilet_units, :gps_clock,
                                :water_cooler_ro_plant_pf_wise, :dustbins, :announcement_system, :two_wheeler_parking_capacity,
                                :four_wheeler_parking_capacity, :pre_paid_taxi_auto_booth, :national_flag, :no_of_daily_trains,
                                :no_of_non_daily_trains, :no_of_functional_uts_counters, :no_of_functional_prs_counters,
                                :ladies_sr_citizen_pwd_uts_counter, :no_of_atvm_available, :no_of_atvm_facilitators,
                                :enquiry_counter, :current_reservation_facility, :no_of_coaches_longest_stopping_train,
                                :paid_lounge_ac, :paid_lounge_non_ac, :waiting_hall_ticketing_area, :retiring_room_nos_ac,
                                :retiring_room_nos_non_ac, :dormitory_gents_beds, :dormitory_ladies_beds, :parcel_office,
                                :no_of_staffs_at_po, :parcel_packing_available, :reserved_vip_lounge_seating_capacity,
                                :upper_class_waiting_room_seating_capacity, :ac_waiting_room_seating_capacity,
                                :general_waiting_room_seating_capacity, :ladies_waiting_room_seating_capacity,
                                :baby_feeding_corner, :medical_emergency_centre, :first_aid_provision, :pharmacy,
                                :battery_operated_cars, :wheel_chair, :trolley_path, :divyang_toilet,
                                :water_sink_pedestal_for_pwd, :no_of_railway_sahayak, :no_of_catering_stall_pf_wise,
                                :no_of_milk_stall_pf_wise, :no_of_multipurpose_stall_pf_wise, :ticket_checking_staff_strength,
                                :osop_stall_location_commodity, :no_of_book_stall_pf_wise, :ttdc, :hpmc,
                                :food_plaza_irctc, :jana_aahar_irctc, :fast_food_unit_irctc, :refreshment_room_irctc,
                                :vrr_nvrr, :electronic_train_indicator_board, :electronic_coach_indication_board,
                                :rdn_video_wall, :manual_coach_indication_board, :rdn_cctv, :wifi_facility,
                                :lifts_with_location_pf_no, :escalator_with_location_pf_no, :brailee_signage,
                                :atm_facility, :grp_out_post, :rpf_post, :sbi_card_kiosk, :gaming_zone,
                                :cleanliness_of_station, :cloak_room, :subway, :mobile_charging_points, :bottle_crusher
                            );
                        """, pa_data)
                        logging.info(f"Inserted/Skipped paavailability for station: {pa_data['station_code']}")
                    except Exception as e:
                        logging.error(f"Error inserting paavailability for station {pa_data['station_code']}: {e}")
                self.conn.commit()
                logging.info("PAAvailability data initialized from CSV.")
            else:
                logging.warning(f"'paavailability.csv' not found in {csv_folder}. Skipping PAAvailability initialization.")
            
            # Initialize works from individual CSV files
            pending_with_files = {
                "Sr.DEN/E/SBC": "SrDEN_E_SBC.csv",
                "Sr.DEN/W/SBC": "SrDEN_W_SBC.csv",
                "Sr.DEN/S/SBC": "SrDEN_S_SBC.csv",
                "Sr.DEN/N/SBC": "SrDEN_N_SBC.csv",
                "Divisional Works": "Divisional_Works.csv",
                "Dy.CE/GSU/SBC": "Dy_CE_GSU_SBC.csv",
                "Sr.DCM/SBC": "SrDCM_SBC.csv"
            }
            
            for key, filename in pending_with_files.items():
                filepath = os.path.join(csv_folder, filename)
                if os.path.isfile(filepath):
                    works_df = pd.read_csv(filepath)
                    for _, row in works_df.iterrows():
                        work_data = {
                            "works_pending_with": key,
                            "project_id": row.get('PROJECTID', '').strip(),
                            "year_of_sanction": int(row.get('Year of Sanction', 0)),
                            "date_of_sanction": row.get('Date of Sanction', '').strip(),
                            "short_name_of_work": row.get('Short Name of Work', '').strip(),
                            "block_section": row.get('Block Section', '').strip(),
                            "station": row.get('Station', '').strip(),
                            "allocation": row.get('ALLOCATION', '').strip(),
                            "cost": float(row.get('Cost', 0.0)),
                            "expenditure_up_to_date": float(row.get('Expenditure upto date', 0.0)),
                            "financial_progress_percent": float(row.get('Financial Progress in %', 0.0)),
                            "if_umbrella": row.get('IF UMBRELLA?', '').strip(),
                            "parent_work": row.get('PARENT WORK', '').strip(),
                            "section": row.get('Section', '').strip(),
                            "remarks": row.get('Remarks', '').strip(),
                            "latest_remarks_civil": row.get('Latest Remarks Civil', '').strip(),
                            "latest_remarks_electrical": row.get('Latest Remarks Electrical', '').strip(),
                            "latest_remarks_s_t": row.get('Latest Remarks S&T', '').strip(),
                            "latest_remarks_civil_as_on": row.get('Latest Remarks Civil As On (DD-MM-YYYY)', '').strip()
                        }
                        try:
                            self.conn.execute("""
                                INSERT OR IGNORE INTO works (
                                    works_pending_with, project_id, year_of_sanction, date_of_sanction, 
                                    short_name_of_work, block_section, station, allocation, cost, 
                                    expenditure_up_to_date, financial_progress_percent, if_umbrella, 
                                    parent_work, section, remarks, latest_remarks_civil, 
                                    latest_remarks_electrical, latest_remarks_s_t, latest_remarks_civil_as_on
                                ) VALUES (
                                    :works_pending_with, :project_id, :year_of_sanction, :date_of_sanction, 
                                    :short_name_of_work, :block_section, :station, :allocation, :cost, 
                                    :expenditure_up_to_date, :financial_progress_percent, :if_umbrella, 
                                    :parent_work, :section, :remarks, :latest_remarks_civil, 
                                    :latest_remarks_electrical, :latest_remarks_s_t, :latest_remarks_civil_as_on
                                );
                            """, work_data)
                            logging.info(f"Inserted/Skipped work record: {work_data['project_id']}")
                        except Exception as e:
                            logging.error(f"Error inserting work record {work_data['project_id']}: {e}")
                    self.conn.commit()
                    logging.info(f"Works data initialized from {filename}.")
                else:
                    logging.warning(f"'{filename}' not found in {csv_folder}. Skipping works initialization for {key}.")
            
            # Initialize remarks from 'remarks.csv' if exists
            remarks_csv = os.path.join(csv_folder, 'remarks.csv')
            if os.path.isfile(remarks_csv):
                remarks_df = pd.read_csv(remarks_csv)
                for _, row in remarks_df.iterrows():
                    remark_data = {
                        "date": row.get('Date', '').strip(),
                        "works_pending_with": row.get('Works Pending with', '').strip(),
                        "project_id": row.get('PROJECTID', '').strip(),
                        "department": row.get('Department', '').strip(),
                        "remark": row.get('Remark', '').strip()
                    }
                    try:
                        self.conn.execute("""
                            INSERT OR IGNORE INTO remarks (
                                date, works_pending_with, project_id, department, remark
                            ) VALUES (
                                :date, :works_pending_with, :project_id, :department, :remark
                            );
                        """, remark_data)
                        logging.info(f"Inserted/Skipped remark for PROJECTID: {remark_data['project_id']}")
                    except Exception as e:
                        logging.error(f"Error inserting remark for PROJECTID {remark_data['project_id']}: {e}")
                self.conn.commit()
                logging.info("Remarks data initialized from CSV.")
            else:
                logging.warning(f"'remarks.csv' not found in {csv_folder}. Skipping remarks initialization.")
            
            logging.info("Data initialization from CSV files completed.")

    if __name__ == "__main__":
        # Example usage
        db = Database()
        manager = WorksManager(db)
        manager.initialize_data_from_csv(csv_folder='.')  # Initialize from current directory
   