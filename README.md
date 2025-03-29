# 🐟 Mad Angler Weather & Fishing Assistant

A weather and fishing assistant script that uses live NOAA data and estimates fishing conditions, water temperature, and fish activity, complete with plots and a GUI display.

## 📦 Requirements

- Python 3.10+ recommended
- Internet connection (for NOAA API and location data)
- Works on Windows, macOS, and Linux

---

## 🔧 Installation

### 1. Install Python

Make sure you have Python installed.

#### ✅ Windows / macOS:

- Go to the official Python website: https://www.python.org/downloads/
- Download the latest **Python 3.x** version for your OS.
- During installation, check **"Add Python to PATH"**.
- Verify it installed correctly:

```bash
python --version
```

#### ✅ Linux (Debian/Ubuntu):

```bash
sudo apt update
sudo apt install python3 python3-pip
```

---

### 2. Clone This Repository

```bash
git clone https://github.com/Kujo016/Mad-Angler-Fishing-Assistant
cd YOUR_REPO_NAME
```

---

### 3. Install Required Python Packages

Install dependencies using `pip`:

```bash
pip install requests geocoder pandas matplotlib tzlocal pytz
```

---

## 🚀 How to Run
Open the python script main.py and enter your email in the "User-Agent": "weather-data-retrieval-script (example@example.com)"
Run the main script from your terminal or command prompt:

```bash
python main.py
```

This will:
- Detect your location
- Fetch weather and fishing data
- Save a CSV and plot images in the `/plots/` folder
- Launch a graphical interface with the latest report

---

## 🗂 Output Files

Saved to:  
`/plots/YYYY-MM-DD/HH-MM/`

Includes:
- `weather_data.csv`
- `temperature_plot.png`
- `pressure_plot.png`
- `humidity_plot.png`
- `wind_speed_plot.png`
- `chart_plot.png`

---

## 🐛 Troubleshooting

If something goes wrong:
- Ensure you're connected to the internet
- Make sure you installed all required libraries
- Check for permission issues creating folders
- Try running with admin privileges if needed
