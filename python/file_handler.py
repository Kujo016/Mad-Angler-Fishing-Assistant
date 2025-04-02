import os
import ctypes
import csv

def run_cpp_function(script_dir, dll_path):

    if not os.path.exists(dll_path):
        raise FileNotFoundError(f"DLL file not found at path: {dll_path}")

    os.add_dll_directory(r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\bin")
    os.add_dll_directory(r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\lib\x64")
    os.add_dll_directory(r"C:\vcpkg\installed\x64-windows\lib")
    os.add_dll_directory(r"C:\vcpkg\installed\x64-windows\bin")

    # Load the DLL
    try:
        mylib = ctypes.WinDLL(dll_path)
        print("DLL loaded successfully!")
    except OSError as e:
        print(f"Failed to load DLL: {e}")

    # Check for function
    if not hasattr(mylib, 'run'):
        raise AttributeError("Function 'run' not found in the DLL.")

    # Construct paths
    directory = os.path.join(script_dir, "AI", "targetFile").encode('utf-8')

    tag_file = b"AI\\tags\\tags.txt"
    code_file = b"AI\\tags\\code_tags.txt"

    mylib.run(directory, tag_file, code_file)

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

def parse_weather_csvs(plots_dir, dll_path):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Load DLL
    try:
        mylib = ctypes.WinDLL(dll_path)
    except Exception as e:
        print(f"Failed to load DLL: {e}")
        return

    if not hasattr(mylib, 'package_csvs_to_bin'):
        print("DLL does not contain 'package_csvs_to_bin'")
        return

    package_csvs_to_bin = mylib.package_csvs_to_bin
    package_csvs_to_bin.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    package_csvs_to_bin.restype = None

    latest_data_folder = get_latest_weather_data_folder(plots_dir)

    # Output .bin file goes here
    
    output_bin = os.path.join(latest_data_folder, "weather_data.bin")
    
    # Call DLL with the cleaned CSV folder
    try:
        package_csvs_to_bin(latest_data_folder.encode('utf-8'), output_bin.encode('utf-8'))
        print("Weather CSVs packaged successfully.")
    except Exception as e:
        print(f"Error calling DLL or computing trajectory: {e}")

#Load csv before displaying it
def load_latest_data():
    base_path = os.path.join('AI', 'targetFile', 'plots')
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
    
def get_latest_weather_data_folder(root_plots_dir):
    latest_file = None
    latest_mtime = -1
    latest_folder = None

    print(f"Walking: {root_plots_dir}")

    for root, dirs, files in os.walk(root_plots_dir):
        for file in files:
            if file == "weather_data.csv":
                full_path = os.path.join(root, file)
                try:
                    mtime = os.path.getmtime(full_path)
                    print(f"Found: {full_path} (mtime={mtime})")
                    if mtime > latest_mtime:
                        latest_mtime = mtime
                        latest_file = full_path
                        latest_folder = os.path.dirname(full_path)
                except Exception as e:
                    print(f"Error reading file time for: {full_path} – {e}")

    if latest_folder:
        print(f"Latest folder: {latest_folder}")
    else:
        print("No valid weather_data.csv found")

    return latest_folder

def get_last_known_data_var():
    base_path = os.path.join('AI', 'targetFile', 'plots')
    if not os.path.exists(base_path):
        print("No saved plots directory found.")
        return None, None, {}

    # Find latest date and time folder
    latest_date = sorted(os.listdir(base_path))[-1]
    latest_time = sorted(os.listdir(os.path.join(base_path, latest_date)))[-1]
    csv_path = os.path.join(base_path, latest_date, latest_time, 'weather_data.csv')

    if not os.path.isfile(csv_path):
        print("No weather data CSV found in the latest folder.")
        return None, None, {}

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reversed(list(reader)):
            try:
                temp = float(row['temperature (F)'])
                humidity = float(row['humidity (%)'])
                pressure = float(row['barometric_pressure (hPa)'])
                wind = float(row['wind_speed (m/s)'])
                if None not in (temp, humidity, pressure, wind):
                    print(f"Recovered valid data from last known row at {latest_date} {latest_time}")
                    return latest_date, latest_time, {
                        'temperature': temp,
                        'humidity': humidity,
                        'pressure': pressure,
                        'wind': wind
                    }
            except (ValueError, TypeError):
                continue

    print("No valid row with complete weather data found.")
    return None, None, {}
