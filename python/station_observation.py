import requests
import geocoder
import pytz
from datetime import datetime
from python import my_math
import math
from python import fish_behavior as fb
from python import file_handler
from python import my_math


# Set a proper User-Agent for NOAA API requests
HEADERS = {"User-Agent": "weather-data-retrieval-script (joshua.kujawa16@outlook.com)"}

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
        est_water_temp = my_math.estimate_water_temp(temp if temp else 60, wind_speed if wind_speed else 0, elevation_ft if elevation_ft else 0)
        fish_note = fb.get_fishing_behavior_advice(est_water_temp, species)
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



def gather_data(dll_path, plots_dir, csv_filename, output_dir):
    lat, lon = get_location()
    station_id = get_station(lat, lon)
    data_list = retrieve_observations(station_id)
    if not data_list:
        print("No observation data retrieved.")
        return
    
    # Step 4: Save full data for display, and single row for charting/trajectory       
    file_handler.save_to_csv(data_list, filename=csv_filename)
    file_handler.parse_weather_csvs(plots_dir, dll_path)
    
    print(f"[INFO] Saving all output to: {output_dir}")
    return data_list