# Mad Angler Fishing Assistant

This is a tool that retrieves weather data from NOAA, estimates fishing conditions, and displays them through a GUI interface. It also includes two batch files to automatically handle Python installation (on Windows) and then run the application.

## Getting Started (Windows)

1. **Download the Project**

   - If you’re on GitHub, click the green “Code” button and select “Download ZIP.”
   - Extract the ZIP contents to any folder on your PC.

2. **Run the Setup**

   - In the extracted folder, find the file named `setup.bat`.
   - **Double-click `setup.bat`** to:
     - Check if Python is installed.
     - (If not installed) Download and install Python (user-level by default).
     - Install or upgrade all required Python libraries (pandas, requests, etc.).
   - If the installation fails due to permissions, **right-click** `setup.bat` and select **“Run as administrator”**. This ensures it can install Python system-wide, if you choose that option.

3. **Run the Application**

   - After the setup completes, run `run.bat`.
   - This will:
     1. Launch Python.
     2. Open `main.py`.
     3. Show a GUI window that fetches your local weather data, generates plots, and displays them in a table.

4. **Output Files**

   - The script automatically creates a subdirectory (like `plots/2025-04-01/10-30/`) or similar, where it saves:
     - `weather_data.csv`
     - `temperature_plot.png`
     - `pressure_plot.png`
     - `humidity_plot.png`
     - `wind_speed_plot.png`
     - A summary chart (`chart_plot.png`) and/or a spiral GIF (`spiral_chart.gif`) if configured.

## Troubleshooting

- **Silent install fails**: If Python can’t install for all users, run `setup.bat` as admin. 
- **No data**: Check internet connectivity; NOAA and geocoder calls require a live connection.
- **Missing DLLs**: If your code references a CUDA or DLL file, ensure it’s present in `bin/` or update the path in your scripts.

Enjoy and tight lines!
