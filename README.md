# 🐟 Mad Angler Weather & Fishing Assistant

A weather and fishing assistant script that uses live NOAA data and estimates fishing conditions, water temperature, and fish activity, complete with plots, code analysis, and a GUI display. Now includes a C++/CUDA backend for scanning source files and tagging relevant code patterns.

---

## 📦 Requirements

### Python Environment
- Python 3.10+ recommended
- Internet connection (for NOAA API and IP-based geolocation)

### Platform Support
- ✅ Windows (full GUI + CUDA support)
- ⚠️ Linux/macOS (weather module works, but CUDA integration not supported yet)

---

## 🔧 Installation

### 1. Install Python

#### ✅ Windows / macOS:
- Download from: https://www.python.org/downloads/
- Check **"Add Python to PATH"** during installation.

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
cd Mad-Angler-Fishing-Assistant
```

---

### 3. Install Required Python Packages

```bash
pip install requests geocoder pandas matplotlib tzlocal pytz
```

---

## ⚙️ C++ / CUDA Backend (for Code Analysis)

This tool also supports analyzing code directories using GPU acceleration (CUDA) and tagging logic.

### 🖥️ Requirements

- ✅ Windows 10 or later
- ✅ Visual Studio 2019+ with Desktop C++ workload
- ✅ CUDA Toolkit v12.8
- ✅ NVIDIA GPU with compute capability
- ✅ vcpkg (for dependencies like `nlohmann/json`)

---

### 🔨 Build the DLL

1. Open **Developer Command Prompt for Visual Studio**
2. Navigate to the repo directory
3. Build the DLL with this command:

```bash
nvcc -o bin/mylib_cud.dll -shared -Xcompiler "/EHsc /LD" dir_tag.cpp kernel.cu -I. -I"path\to\vcpkg\installed\x64-windows\include" -L"path\to\vcpkg\installed\x64-windows\lib"
```

Replace the `path\to\...` parts with your actual vcpkg paths.

> ⚠️ Make sure `kernel.cuh` and `tag_dir.h` are in the include path.

---

## 🚀 Run the Full Program (GUI + Weather + Code Scan)

Use:

```bash
python python/InitGUI.py
```

This will:
- Detect your current location
- Retrieve NOAA weather observations
- Estimate fishing behavior and water temp
- Display conditions and plots in a GUI
- Trigger the C++/CUDA backend to scan your `/AI/targetFile/` folder
- Save analysis output to:
  - `AI/Reports/code_summary_results.json`
  - `AI/Reports/directory_structure_full.txt`

---

## 🗂 Output Files

Saved in:

```
AI/targetFile/plots/YYYY-MM-DD/HH-MM/
```

Includes:
- `weather_data.csv`
- `temperature_plot.png`
- `pressure_plot.png`
- `humidity_plot.png`
- `wind_speed_plot.png`
- `chart_plot.png`

---

## 🧠 Code Summary Output

Saved in:

```
AI/Reports/
├── code_summary_results.json         # Tags and counts for each file
└── directory_structure_full.txt      # Directory map and total file sizes
```

---

## 🐛 Troubleshooting

- Check internet connection for NOAA API
- Run as admin if folder creation fails
- Make sure Python, CUDA, and DLL paths are correct
- Ensure DLL is named `mylib_cud.dll` and placed in `/bin/`

---

## 🗂 Folder Structure Overview

```
your_project/
├── AI/
│   ├── Reports/
│   └── targetFile/
│       └── plots/
├── bin/
│   └── mylib_cud.dll
├── tags/
│   ├── tags.txt
│   └── code_tags.txt
├── python/
│   ├── InitGUI.py
│   ├── main.py
│   └── list_directory_full.py
├── dir_tag.cpp
├── tag_dir.h
├── kernel.cu
├── kernel.cuh
```

---

## 🙌 Author

**Joshua Kujawa** – Mad Angler Publishing
