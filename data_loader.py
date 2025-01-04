import pandas as pd
import logging

class DataLoader:
    def __init__(self, station_csv: str, works_csv: str):
        self.station_csv = station_csv
        self.works_csv = works_csv

    def load_station_data(self):
        """Load and prepare station data."""
        try:
            station_data = pd.read_csv(self.station_csv)
            station_data.columns = [
                col.strip().upper().replace(" ", "_") for col in station_data.columns
            ]
            station_data.fillna("", inplace=True)
            station_data["DISPLAY_NAME"] = station_data.apply(
                lambda row: f"{row['STATION_NAME']} ({row['STATION_CODE']})", axis=1
            )
            return station_data
        except Exception as e:
            logging.error(f"Error loading station data: {e}")
            raise

    def load_works_data(self):
        """Load and normalize works data."""
        try:
            works_data = pd.read_csv(self.works_csv)
            expanded_rows = []
            for _, row in works_data.iterrows():
                stations = str(row["Station"]).split(",")
                for station in stations:
                    station = station.strip()
                    new_row = row.copy()
                    new_row["Station"] = station
                    expanded_rows.append(new_row)
            return pd.DataFrame(expanded_rows)
        except Exception as e:
            logging.error(f"Error loading works data: {e}")
            raise