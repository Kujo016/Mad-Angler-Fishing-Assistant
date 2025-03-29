import os
import pytz
import requests
import geocoder
import csv
from datetime import datetime
import math
import pandas as pd
import matplotlib.pyplot as plt
from zoneinfo import ZoneInfo
import tzlocal 
import tkinter as tk
from tkinter import ttk, scrolledtext


# Set a proper User-Agent for NOAA API requests
HEADERS = {"User-Agent": "weather-data-retrieval-script (example@example.com)"}

def get_location():
    g = geocoder.ip('me')
    if g.ok and g.latlng:
        lat, lon = g.latlng
        print(f"Detected location: Latitude {lat}, Longitude {lon}")
        return lat, lon
    else:
        print("Failed to get location.")
        raise Exception("Could not determine device location.")

def get_station(lat, lon):
    points_url = f"https://api.weather.gov/points/{lat},{lon}"
    print(f"Requesting gridpoint data from: {points_url}")
    response = requests.get(points_url, headers=HEADERS)
    response.raise_for_status()
    points_data = response.json()
    stations_url = points_data['properties']['observationStations']
    print(f"Requesting stations data from: {stations_url}")
    station_resp = requests.get(stations_url, headers=HEADERS)
    station_resp.raise_for_status()
    stations_data = station_resp.json()
    if stations_data['features']:
        station_id = stations_data['features'][0]['properties']['stationIdentifier']
        print(f"Using observation station: {station_id}")
        return station_id
    else:
        print("No observation stations found.")
        raise Exception("No observation stations found for the location.")

def retrieve_observations(station_id, max_results=50):
    obs_url = f"https://api.weather.gov/stations/{station_id}/observations"
    response = requests.get(obs_url, headers=HEADERS)
    response.raise_for_status()
    obs_data = response.json()
    observations = obs_data.get('features', [])[:max_results]
    data_list = []
    for feature in observations:
        props = feature['properties']
        timestamp = props.get('timestamp')
        if not timestamp:
            continue
        dt_utc = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        if dt_utc.tzinfo is None:
            dt_utc = pytz.utc.localize(dt_utc)
        dt = dt_utc.astimezone(pytz.timezone('America/Boise'))
        date_str = dt.date().isoformat()
        time_str = dt.time().strftime('%H:%M')
        temp_temp = props.get('temperature', {}).get('value')
        temp = (temp_temp * 9/5 + 32) if temp_temp is not None else None
        pressure = props.get('barometricPressure', {}).get('value')
        pressure_hpa = pressure / 100.0 if pressure is not None else None
        description = props.get('textDescription')
        dewpoint = props.get('dewpoint', {}).get('value')
        if temp is not None and dewpoint is not None:
            rh = 100 * (math.exp((17.625 * dewpoint)/(243.04 + dewpoint)) / 
                        math.exp((17.625 * temp)/(243.04 + temp)))
        else:
            rh = None
        wind_speed = props.get('windSpeed', {}).get('value')
        wind_dir = props.get('windDirection', {}).get('value')
        dew_c = props.get('dewpoint', {}).get('value')
        dew_f = (dew_c * 9/5 + 32) if dew_c is not None else None
        visibility_m = props.get('visibility', {}).get('value')
        visibility_miles = visibility_m / 1609.344 if visibility_m is not None else None
        cloud_layers = props.get('cloudLayers', [])
        cloud_cover = cloud_layers[0].get('amount') if cloud_layers else None
        ceiling_m = props.get('ceiling', {}).get('value')
        ceiling_ft = ceiling_m * 3.28084 if ceiling_m is not None else None
        heat_index_c = props.get('heatIndex', {}).get('value')
        heat_index_f = (heat_index_c * 9/5 + 32) if heat_index_c is not None else None
        wind_chill_c = props.get('windChill', {}).get('value')
        wind_chill_f = (wind_chill_c * 9/5 + 32) if wind_chill_c is not None else None
        precip_mm = props.get('precipitationLastHour', {}).get('value')
        precip_in = precip_mm / 25.4 if precip_mm is not None else None
        elevation_m = props.get('elevation', {}).get('value')
        elevation_ft = elevation_m * 3.28084 if elevation_m is not None else None
        station_url = props.get('station')
        station_name = station_url.split('/')[-1] if station_url else None
        species = "Coldwater (e.g., trout)" if elevation_ft and elevation_ft >= 4000 else "Warmwater (e.g., bass)"
        est_water_temp = estimate_water_temp(temp if temp else 60, wind_speed if wind_speed else 0, elevation_ft if elevation_ft else 0)
        fish_note = get_fishing_behavior_advice(est_water_temp, species)
        pressure_trend = "N/A"
        if len(data_list) >= 1:
            last_pressure = data_list[-1].get("barometric_pressure (hPa)")
            if last_pressure and pressure_hpa:
                pressure_trend = "Rising" if pressure_hpa > last_pressure else "Falling"
        data_list.append({
            "date": date_str,
            "time": time_str,
            "temperature (F)": temp,
            "humidity (%)": rh,
            "barometric_pressure (hPa)": pressure_hpa,
            "weather": description,
            "wind_speed (m/s)": wind_speed,
            "wind_direction (°)": wind_dir,
            "dew_point (F)": dew_f,
            "visibility (mi)": visibility_miles,
            "cloud_cover": cloud_cover,
            "ceiling (ft)": ceiling_ft,
            "heat_index (F)": heat_index_f,
            "wind_chill (F)": wind_chill_f,
            "precipitation_last_hour (in)": precip_in,
            "station_elevation (ft)": elevation_ft,
            "station_name": station_name,
            "species_target": species,
            "estimated_water_temp (F)": est_water_temp,
            "fishing_note": fish_note,
            "pressure_trend": pressure_trend
        })
    return data_list

def save_to_csv(data_list, filename):
    fieldnames = [
        "date", "time", "temperature (F)", "humidity (%)",
        "barometric_pressure (hPa)", "weather",
        "wind_speed (m/s)", "wind_direction (°)",
        "dew_point (F)", "visibility (mi)", "cloud_cover", "ceiling (ft)",
        "heat_index (F)", "wind_chill (F)", "precipitation_last_hour (in)",
        "station_elevation (ft)", "station_name",
        "species_target", "estimated_water_temp (F)", "fishing_note", "pressure_trend"
    ]
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data_list:
            writer.writerow(row)
    print(f"Data saved to {filename}")


def plot_weather_data(csv_filename, date_str, time_str):
    # Read CSV file into a pandas DataFrame
    df = pd.read_csv(csv_filename, encoding='utf-8-sig')
    
    # Combine date and time columns into a datetime column and sort by time
    df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])
    df.sort_values('datetime', inplace=True)
    
    # Plot Temperature over time
    plt.figure()
    plt.plot(df['datetime'], df['temperature (F)'], marker='o')
    plt.xlabel('Time')
    plt.ylabel('Temperature (°F)')
    plt.title('Temperature Over Time')
    plt.xticks(rotation=45)
    plt.tight_layout()
    t_plot_path = os.path.join('plots', date_str, time_str, 'temperature_plot.png')
    plt.savefig(t_plot_path)
    plt.show(block=False)
    plt.pause(0.1)

    print(f"Temperature plot saved as '{t_plot_path}'")

    
    # Plot Barometric Pressure over time
    plt.figure()
    plt.plot(df['datetime'], df['barometric_pressure (hPa)'], marker='o')
    plt.xlabel('Time')
    plt.ylabel('Barometric Pressure (hPa)')
    plt.title('Barometric Pressure Over Time')
    plt.xticks(rotation=45)
    plt.tight_layout()
    bp_plot_path = os.path.join('plots', date_str, time_str, 'pressure_plot.png')
    plt.savefig(bp_plot_path)
    plt.show(block=False)
    plt.pause(0.1)

    print(f"Pressure plot saved as '{bp_plot_path}'")

    
    # Plot Humidity over time (if data available)
    if df['humidity (%)'].notnull().any():
        plt.figure()
        plt.plot(df['datetime'], df['humidity (%)'], marker='o')
        plt.xlabel('Time')
        plt.ylabel('Relative Humidity (%)')
        plt.title('Relative Humidity Over Time')
        plt.xticks(rotation=45)
        plt.tight_layout()
        h_plot_path = os.path.join('plots', date_str, time_str, 'humidity_plot.png')
        plt.savefig(h_plot_path)
        plt.show(block=False)
        plt.pause(0.1)

        print(f"Humidity plot saved as '{h_plot_path}'")

    else:
        print("No humidity data available to plot.")
    
    
    # Plot Wind Speed over time (if data available)
    if 'wind_speed (m/s)' in df.columns and df['wind_speed (m/s)'].notnull().any():
        plt.figure()
        plt.plot(df['datetime'], df['wind_speed (m/s)'], marker='o')
        plt.xlabel('Time')
        plt.ylabel('Wind Speed (m/s)')
        plt.title('Wind Speed Over Time')
        plt.xticks(rotation=45)
        plt.tight_layout()
        w_plot_path = os.path.join('plots', date_str, time_str, 'wind_speed_plot.png')
        plt.savefig(w_plot_path)
        plt.show(block=False)
        plt.pause(0.1)

        print(f"Wind speed plot saved as '{w_plot_path}'")
    else:
        print("No wind speed data available to plot.")
#Water Temp
def estimate_water_temp(air_temp, wind_speed, elevation_ft):
    base = air_temp - (wind_speed * 0.5 if wind_speed else 0)
    if elevation_ft and elevation_ft > 5000:
        base -= 5
    return round(base, 1)
#Fish Behavior
def get_fishing_behavior_advice(water_temp, species_type):
    if species_type == "Coldwater (e.g., trout)":
        if 50 <= water_temp <= 65:
            return "Prime trout activity."
        elif water_temp < 45:
            return "Trout sluggish – use small flies."
        elif water_temp > 68:
            return "Danger zone – fish early or go higher."
    elif species_type == "Warmwater (e.g., bass)":
        if 65 <= water_temp <= 78:
            return "Aggressive bass – try topwater or streamers."
        elif water_temp < 60:
            return "Cold front – slow retrieves deep."
        elif water_temp > 85:
            return "Seek shade, structure – fish are stressed."
    return "Marginal conditions."

# Define quadrant coordinates for each condition
base_tags = {
    'a': {'label': 'Calm, Low Fish Activity', 'point': [-1, 1]},
    'e': {'label': 'Subtle Shift (Chilly Breeze)', 'point': [-1, 0]},
    'b': {'label': 'Ideal Fishing Window', 'point': [1, 1]},
    'f': {'label': 'Drop In Conditions', 'point': [0, 1]},
    'c': {'label': 'Challenging, Fish May Bite', 'point': [-1, -1]},
    'g': {'label': 'Lift In Conditions', 'point': [1, 0]},
    'd': {'label': 'Chaotic, Unpredictable', 'point': [1, -1]},
    'h': {'label': 'High Pressure Returning', 'point': [0, -1]},
    'x': {'label': 'Calm Conditons', 'point': [0, 0]}
}

def spiral_position_from_vector(vector, humidity, pressure, temp, wind):
    # Normalize inputs
    norm_humidity = max(min(humidity / 100.0, 1.0), 0.01)
    norm_temp = (temp * humidity) / pressure
    norm_wind = (wind * humidity) / pressure

    # Spiral logic
    r = norm_humidity * norm_temp
    theta = 2 * math.pi * norm_wind

    # Spiral outputs (not biased yet)
    spiral_x = r * math.cos(theta)
    spiral_y = r * math.sin(theta)

    # Now scale the spiral by the condition vector
    x = vector[0] * spiral_x 
    y = vector[1] * spiral_y 

    return x, y


def classify_conditions(temp, humidity, pressure, wind):
    if 55 <= temp <= 65 and wind < 10 and pressure >= 1015 and humidity < 30:
        return 'a'
    elif 60 <= temp <= 75 and 40 <= humidity <= 70 and pressure >= 1010 and 5 <= wind <= 15:
        return 'b'
    elif 70 <= temp <= 80 and humidity > 60 and wind >= 15 and pressure < 1010:
        return 'c'
    elif temp > 80 or temp < 40 or wind > 25 or humidity > 85 or humidity < 20 or pressure < 1005:
        return 'd'
    elif 50 <= temp <= 60 and 30 <= humidity <= 50 and wind <= 12 and pressure >= 1010:
        return 'e'
    elif 65 <= temp <= 72 and 60 <= humidity <= 80 and pressure >= 1012 and wind <= 5:
        return 'f'
    elif 60 <= temp <= 70 and humidity > 70 and 10 <= wind <= 18 and 1005 <= pressure <= 1010:
        return 'g'
    elif 45 <= temp <= 55 and 40 <= humidity <= 70 and 1005 <= pressure <= 1015:
        return 'h'
    else:
        return 'x'

def chart_run(data_list, date_str, time_str):
    current_temp = data_list[2]['temperature (F)'] 
    current_humidity = data_list[3]['humidity (%)']
    current_pressure = data_list[4]['barometric_pressure (hPa)']
    current_wind = data_list[6]['wind_speed (m/s)']
    
    zone = classify_conditions(current_temp, current_humidity, current_pressure, current_wind)
    direction_vector = base_tags[zone]['point']
    spiral_x, spiral_y = spiral_position_from_vector(direction_vector, current_humidity, current_pressure, current_temp, current_wind)
    chart = plt.figure(figsize=(8, 8))
    for key, info in base_tags.items():
        plt.scatter(*info['point'], label=f"{key.upper()}: {info['label']}", s=100)
        plt.text(info['point'][0]+0.05, info['point'][1]+0.05, key.upper(), fontsize=12)

    plt.scatter(spiral_x, spiral_y, color='red', edgecolor='black', s=200, label='Current Condition (Spiral)')

    plt.axhline(0, color='black', linewidth=0.5)
    plt.axvline(0, color='black', linewidth=0.5)
    plt.title("Fishing Condition Map")
    plt.xlabel("Condition Axis (Worst to Best Conditions)")
    plt.ylabel("Activity Axis (Least to Most Active)")
    plt.grid(True)
    plt.legend()
    plt.axis('equal')
    plt.tight_layout()
    fig_plot_path = os.path.join('plots', date_str, time_str, 'chart_plot.png')
    plt.savefig(fig_plot_path)
    plt.show(block=False)
    plt.pause(0.1)

    return chart

def load_latest_data():
    base_path = "plots"
    if not os.path.exists(base_path):
        return []

    # Find latest folder
    latest_date = sorted(os.listdir(base_path))[-1]
    latest_time = sorted(os.listdir(os.path.join(base_path, latest_date)))[-1]
    csv_path = os.path.join(base_path, latest_date, latest_time, 'weather_data.csv')

    if not os.path.isfile(csv_path):
        return []

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        return list(reader)

def display_data(window, data_list):
    if not data_list:
        tk.Label(window, text="No data available.", foreground="red").pack()
        return

    columns = list(data_list[0].keys())

    tree = ttk.Treeview(window, columns=columns, show='headings', height=20)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=140, anchor='center')

    for row in data_list:
        values = [row[col] for col in columns]
        tree.insert('', tk.END, values=values)

    tree.pack(padx=10, pady=10, fill='both', expand=True)

def main():
    try:
        lat, lon = get_location()
        station_id = get_station(lat, lon)
        data_list = retrieve_observations(station_id)
        if not data_list:
            print("No observation data retrieved.")
            return

        local_tz = ZoneInfo(tzlocal.get_localzone_name())
        local_now = datetime.now(local_tz)

        date_str = local_now.strftime('%Y-%m-%d')
        time_str = local_now.strftime('%H-%M')

        # Save CSV file to unique path
        output_dir = os.path.join('plots', date_str, time_str)
        os.makedirs(output_dir, exist_ok=True)
        csv_filename = os.path.join(output_dir, 'weather_data.csv')
        save_to_csv(data_list, filename=csv_filename)
        print(f"Saving all output to: {output_dir}")
        # Plot using those values
        plot_weather_data(csv_filename, date_str, time_str)
        #Run Chart
        chart_run(data_list, date_str, time_str)
        #Run GUI
        root = tk.Tk()
        root.title("Mad Angler Weather & Fishing Assistant")
        root.geometry("1600x600")

        title = tk.Label(root, text="Latest Fishing Conditions Report", font=("Helvetica", 18, "bold"))
        title.pack(pady=10)

        data = load_latest_data()
        display_data(root, data)

        root.mainloop()

        #Terminate
        print(f"END PROGRAM")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    

if __name__ == "__main__":
    main()