import pandas as pd
import os

from src.api.tfl import get_bike_points, process_bike_points

def collect_and_save():
    print("fetching live TFL data...")
    raw_data = get_bike_points()
    processed_data = process_bike_points(raw_data)

    df = pd.DataFrame(processed_data)

    # Round timestamp down to nearest 15 minutes
    # Guarantess it will join with the Open-Meteo weather data later
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.floor('15min')

    os.makedirs("data", exist_ok=True)
    file_path = "data/tfl_live_data.csv"

    if os.path.exists(file_path):
        df.to_csv(file_path, mode = 'a', header = False, index = False)
        print(f"Appended {len(df)} rows to {file_path}")
    else:
        df.to_csv(file_path, mode = 'w', header = True, index = False)
        print(f"Created new dataset with {len(df)} rows at {file_path}")

if __name__ == "__main__":
    collect_and_save()
