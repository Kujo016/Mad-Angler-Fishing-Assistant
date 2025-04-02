import os
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.animation as animation
from matplotlib.patches import Circle
from python import  weather
from python import  my_math
from python import file_handler


def chart_gif(gif_dir):
    data_list = file_handler.load_latest_data()
    fig, ax = plt.subplots(figsize=(8, 8))

    line, = ax.plot([], [], lw=2, color='blue')
    point_marker, = ax.plot([], [], 'ro', markersize=8)

    ax.axhline(0, color='black', linewidth=0.5)
    ax.axvline(0, color='black', linewidth=0.5)
    
    ax.set_xlabel("Condition Axis")
    ax.set_ylabel("Activity Axis")
    ax.grid(True)
    ax.axis('equal')

    # Plot base zones
    for key, info in weather.base_tags.items():
        ax.scatter(*info['point'], label=f"{key.upper()}: {info['label']}", s=100)
        ax.text(info['point'][0]+0.05, info['point'][1]+0.05, key.upper(), fontsize=12)
    
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)

    # Find latest valid data row
    sorted_rows = sorted(data_list, key=lambda r: f"{r['date']} {r['time']}", reverse=True)
    for row in sorted_rows:
        try:
            current_temp = float(row['temperature (F)'])
            current_humidity = float(row['humidity (%)'])
            current_pressure = float(row['barometric_pressure (hPa)'])
            current_wind = float(row['wind_speed (m/s)'])
            if all(val is not None for val in (current_temp, current_humidity, current_pressure, current_wind)):
                break
        except (ValueError, TypeError):
            continue
    else:
        print("No complete weather data found. Aborting GIF rendering.")
        return

    ax.set_title(f"Fishing Condition Spiral GIF\n{row['date']} {row['time']}")
    zone = weather.classify_conditions(current_temp, current_humidity, current_pressure, current_wind)
    direction_vector = weather.base_tags[zone]['point']

    # Generate spiral trail
    spiral_trail = []
    t_steps = 100
    for t in range(t_steps):
        point = my_math.spiral_position_within_quadrant(
            current_temp,
            current_humidity,
            current_pressure,
            direction_vector,
            current_wind,
            t=t / 10.0
        )
        spiral_trail.append(point)

    def init():
        line.set_data([], [])
        point_marker.set_data([], [])
        return line, point_marker

    def animate(i):
        if i == 0:
            return line, point_marker
        x_vals, y_vals = zip(*spiral_trail[:i+1])
        line.set_data(x_vals, y_vals)
        point_marker.set_data([x_vals[-1]], [y_vals[-1]])
        return line, point_marker

    # Disable blit for better compatibility with text/axes
    ani = animation.FuncAnimation(
        fig, animate,
        frames=len(spiral_trail),
        init_func=init,
        blit=False,
        interval=50
    )

    
    os.makedirs(gif_dir, exist_ok=True)
    gif_path = os.path.join(gif_dir, 'spiral_chart.gif')
    ani.save(gif_path, writer='pillow')
    plt.close()
    print(f"GIF saved to {gif_path}")

def chart_run(output_dir, date_str, time_str):
    data_list = file_handler.load_latest_data()
    # Find the latest complete row from the end of the list
    sorted_rows = sorted(data_list, key=lambda r: f"{r['date']} {r['time']}", reverse=True)
    for row in sorted_rows:
        try:
            current_temp = float(row['temperature (F)'])
            current_humidity = float(row['humidity (%)'])
            current_pressure = float(row['barometric_pressure (hPa)'])
            current_wind = float(row['wind_speed (m/s)'])
            if all(val is not None for val in (current_temp, current_humidity, current_pressure, current_wind)):
                break
        except (ValueError, TypeError):
            continue
    else:
        print("Missing or incomplete data. Attempting to recover from last known valid entry...")
        last_date, last_time, recovered = file_handler.get_last_known_data_var()
        if recovered:
            current_temp = recovered['temperature']
            current_humidity = recovered['humidity']
            current_pressure = recovered['pressure']
            current_wind = recovered['wind']
            date_str = last_date or date_str
            time_str = last_time or time_str
        else:
            print("Failed to recover valid data. Aborting chart rendering.")
            return

    zone = weather.classify_conditions(current_temp, current_humidity, current_pressure, current_wind)
    direction_vector = weather.base_tags[zone]['point']

    # Generate the spiral trail
    spiral_trail = []
    t_steps = 100
    for t in range(t_steps):
        point = my_math.spiral_position_within_quadrant(
            current_temp,
            current_humidity,
            current_pressure,
            direction_vector,
            current_wind,
            t=t / 10.0
        )
        spiral_trail.append(point)

    spiral_x, spiral_y = spiral_trail[-1]

    # Begin chart drawing
    chart = plt.figure(figsize=(8, 8))

    # Plot base zones
    for key, info in weather.base_tags.items():
        plt.scatter(*info['point'], label=f"{key.upper()}: {info['label']}", s=100)
        plt.text(info['point'][0]+0.05, info['point'][1]+0.05, key.upper(), fontsize=12)

    # Plot spiral trail and final point
    trail_x, trail_y = zip(*spiral_trail)
    plt.plot(trail_x, trail_y, color='blue', linewidth=2, label='Spiral Path')
    plt.scatter(spiral_x, spiral_y, color='red', edgecolor='black', s=200, label='Current Condition (Spiral)')

    # Axes and labels
    plt.axhline(0, color='black', linewidth=0.5)
    plt.axvline(0, color='black', linewidth=0.5)
    plt.title(f"Fishing Condition Map\n{row['date']} {row['time']}")
    plt.xlabel("Condition Axis (Worst to Best Conditions)")
    plt.ylabel("Activity Axis (Least to Most Active)")
    plt.grid(True)
    plt.legend()
    plt.axis('equal')
    plt.tight_layout()

    # Save and show
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_dir), exist_ok=True)
    save_fig = os.path.join(output_dir, 'chaos_chart.png')
    plt.savefig(save_fig)
    plt.show(block=False)
    plt.pause(0.1)

    return chart

def chart_prediction_run(plots_dir, traj_bin_file_path, predicted_sequence, date_str, time_str):
    if not predicted_sequence:
        print("[ERROR] No predicted sequence to chart.")
        return

    print(f"[INFO] Plotting predicted quadrant sequence: {predicted_sequence}")

    # Begin chart drawing
    chart = plt.figure(figsize=(8, 8))

    # Plot base zones
    for key, info in weather.base_tags.items():
        plt.scatter(*info['point'], label=f"{key.upper()}: {info['label']}", s=100)
        plt.text(info['point'][0] + 0.05, info['point'][1] + 0.05, key.upper(), fontsize=12)

    # Simulate spiral trail for predicted zones
    spiral_trail = []
    dummy_temp, dummy_humidity, dummy_pressure, dummy_wind = traj.get_average_trajectory_values(traj_bin_file_path)

    for step, q in enumerate(predicted_sequence):
        if q not in weather.base_tags:
            print(f"[WARNING] Unknown quadrant '{q}' in prediction sequence. Skipping.")
            continue

        direction_vector = weather.base_tags[q]['point']
        t = step / 10.0
        spiral_point = my_math.spiral_position_within_quadrant(
            dummy_temp,
            dummy_humidity,
            dummy_pressure,
            direction_vector,
            dummy_wind,
            t
        )
        spiral_trail.append(spiral_point)


    if not spiral_trail:
        print("[ERROR] Spiral trail is empty. Nothing to plot.")
        return

    # Extract x and y coordinates from trail
    trail_x, trail_y = zip(*spiral_trail)

    # Calculate center of the cluster (mean)
    center_x = sum(trail_x) / len(trail_x)
    center_y = sum(trail_y) / len(trail_y)

    # Calculate a radius (max distance from center to any point)
    radius = (max(((x - center_x)**2 + (y - center_y)**2)**0.5 for x, y in spiral_trail))/2

    # Draw the cluster circle
    circle = Circle((center_x, center_y), radius, color='red', alpha=0.3, label='Predicted Cluster')
    plt.gca().add_patch(circle)

    # Optionally mark the center
    plt.scatter(center_x, center_y, color='black', s=150, label='Predicted Cluster Center')


    # Axes and labels
    plt.axhline(0, color='black', linewidth=0.5)
    plt.axvline(0, color='black', linewidth=0.5)
    plt.title(f"Predicted Fishing Path\n{date_str} {time_str}")
    plt.xlabel("Condition Axis (Worst to Best Conditions)")
    plt.ylabel("Activity Axis (Least to Most Active)")
    plt.grid(True)
    plt.legend()
    plt.axis('equal')

    # Safe directory handling
    save_folder = os.path.join(plots_dir, date_str, time_str)
    os.makedirs(save_folder, exist_ok=True)

    # Save with timestamped or unique filename
    fig_plot_path = os.path.join(save_folder, f"predicted_chart.png")
    plt.savefig(fig_plot_path)
    print(f"[INFO] Prediction chart saved at: {fig_plot_path}")
    plt.show(block=False)
    plt.pause(0.1)

    return chart


def plot_weather_data(output_dir, csv_filename):
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
    t_plot_path = os.path.join(output_dir, 'temperature_plot.png')
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
    bp_plot_path = os.path.join(output_dir, 'pressure_plot.png')
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
        h_plot_path = os.path.join(output_dir, 'humidity_plot.png')
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
        w_plot_path = os.path.join(output_dir, 'wind_speed_plot.png')
        plt.savefig(w_plot_path)
        plt.show(block=False)
        plt.pause(0.1)

        print(f"Wind speed plot saved as '{w_plot_path}'")
    else:
        print("No wind speed data available to plot.")
