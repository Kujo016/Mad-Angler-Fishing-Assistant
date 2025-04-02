import os
import ctypes
from python import my_display
from python import station_observation
from zoneinfo import ZoneInfo
import tzlocal
from datetime import datetime

if __name__ == "__main__":
    # Get the script's actual directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    plots_dir = os.path.join(script_dir, "AI", "targetFile", "plots")    
    
    # Construct the correct DLL path
    dll_path = os.path.join(script_dir, "bin", "OmniBase.dll")
    
    # Setup paths & timestamps
    local_tz = ZoneInfo(tzlocal.get_localzone_name())
    local_now = datetime.now(local_tz)
    date_str = local_now.strftime('%Y-%m-%d')
    time_str = local_now.strftime('%H-%M')
    output_dir = os.path.join('AI', 'targetFile', 'plots', date_str, time_str)
    os.makedirs(output_dir, exist_ok=True)
    csv_filename = os.path.join(output_dir, 'weather_data.csv')

    #Prepare trajectory file paths
    input_path = os.path.join(output_dir, "weather_data.bin")
    output_path = os.path.join(output_dir, "trajectory_data.bin")
    

    #Gather Data
    station_observation.gather_data(dll_path, plots_dir, csv_filename, input_path, output_path, output_dir)

    my_display.deploy(script_dir, dll_path, plots_dir, output_dir, date_str, time_str, csv_filename, input_path, output_path)
