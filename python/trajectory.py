import os
import ctypes
import struct
import math
import matplotlib.pyplot as plt
from python import file_handler
from python import chart

def load_and_plot_trajectory(plots_dir, traj_bin_file_path, dll_path, input_path, output_path):
    
    point_struct = struct.Struct('fffif')  # 20 bytes per point
    trajectory_points = []

    # Read the binary file
    try:
        with open(traj_bin_file_path, 'rb') as f:
            count_bytes = f.read(4)
            if len(count_bytes) < 4:
                print("[ERROR] File too short to contain a point count.")
                return

            point_count = struct.unpack('I', count_bytes)[0]
            print(f"[INFO] Point count from header: {point_count}")

            expected_bytes = point_count * point_struct.size
            actual_bytes = os.path.getsize(traj_bin_file_path) - 4
            print(f"[DEBUG] Expected data bytes: {expected_bytes}, actual: {actual_bytes}")

            if actual_bytes < expected_bytes:
                print("[WARNING] File may be truncated or corrupted.")

            for i in range(point_count):
                chunk = f.read(point_struct.size)
                if len(chunk) < point_struct.size:
                    print(f"[WARNING] Stopped early at index {i}, incomplete chunk.")
                    break
                dx, dy, dz, quadrant, magnitude = point_struct.unpack(chunk)
                if any(map(lambda x: not isinstance(x, float) or not x == x, (dx, dy, dz))):
                    print(f"[WARNING] NaN or invalid vector at index {i}, skipping.")
                    continue
                trajectory_points.append((dx, dy, dz, quadrant, magnitude))

    except FileNotFoundError:
        print(f"[ERROR] Trajectory file not found: {traj_bin_file_path}")
        return

    if not trajectory_points:
        print("[ERROR] No trajectory points were loaded.")
        return

    # Plotting
    dxs, dys, dzs, quadrants, magnitudes = zip(*trajectory_points)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    try:
        ax.quiver(
            [0]*len(dxs), [0]*len(dys), [0]*len(dzs),
            dxs, dys, dzs,
            length=1.0, normalize=True, color='blue', linewidth=0.5
        )
        ax.set_xlabel('dx - Temperature')
        ax.set_ylabel('dy - Humidity')
        ax.set_zlabel('dz - Pressure')
        ax.set_title('Measure of Environment\'s Force Field')
        print("[INFO] 3D plot generated successfully.")
        
        latest_folder = file_handler.get_latest_weather_data_folder(plots_dir)
        save_path = os.path.join(latest_folder, "trajectory.png")
        plt.savefig(save_path)
        print(f"[INFO] Plot saved at {save_path}")
        
        plt.show()



    except Exception as e:
        print(f"[ERROR] Failed to plot vectors: {e}")

def get_last_trajectory_point(bin_file_path):
    import struct
    import os

    point_struct = struct.Struct('fffif')

    if not os.path.exists(bin_file_path):
        print("[ERROR] Trajectory file not found.")
        return None

    try:
        with open(bin_file_path, 'rb') as f:
            header = f.read(4)
            if len(header) < 4:
                print("[ERROR] Header too short.")
                return None

            point_count = struct.unpack('I', header)[0]
            if point_count == 0:
                print("[WARNING] No data points found.")
                return None

            # SEEK based on record index, not from file end
            seek_pos = 4 + (point_count - 1) * point_struct.size
            f.seek(seek_pos)
            data = f.read(point_struct.size)
            if len(data) != point_struct.size:
                print("[ERROR] Incomplete final record.")
                return None

            dx, dy, dz, quadrant, magnitude = point_struct.unpack(data)
            return dx, dy, dz, quadrant, magnitude

    except Exception as e:
        print(f"[ERROR] Failed to read last trajectory point: {e}")
        return None


def get_prediction_traj(dll_path, traj_bin_path, buffer_size=32):
    if not os.path.exists(dll_path):
        raise FileNotFoundError(f"DLL not found at {dll_path}")
    if not os.path.exists(traj_bin_path):
        raise FileNotFoundError(f"Trajectory binary not found at {traj_bin_path}")

    try:
        mylib = ctypes.WinDLL(dll_path)
        get_predicted_quadrants = mylib.get_predicted_quadrants
        get_predicted_quadrants.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
        get_predicted_quadrants.restype = None

        buffer = ctypes.create_string_buffer(buffer_size)
        get_predicted_quadrants(traj_bin_path.encode('utf-8'), buffer, buffer_size)

        predicted = buffer.value.decode('utf-8')
        print(f"Predicted Quadrants: {predicted}")
        return predicted

    except Exception as e:
        print(f"[ERROR] Failed to call get_predicted_quadrants: {e}")
        return None

def display_traj_prediction(plots_dir, predicted_quads, traj_bin_file_path, dll_path, input_path, output_path):

    point_struct = struct.Struct('fffif')  # 20 bytes per point
    trajectory_points = []

    # Read the binary file
    try:
        with open(traj_bin_file_path, 'rb') as f:
            count_bytes = f.read(4)
            if len(count_bytes) < 4:
                print("[ERROR] File too short to contain a point count.")
                return

            point_count = struct.unpack('I', count_bytes)[0]
            print(f"[INFO] Point count from header: {point_count}")

            expected_bytes = point_count * point_struct.size
            actual_bytes = os.path.getsize(traj_bin_file_path) - 4
            print(f"[DEBUG] Expected data bytes: {expected_bytes}, actual: {actual_bytes}")

            if actual_bytes < expected_bytes:
                print("[WARNING] File may be truncated or corrupted.")

            for i in range(point_count):
                chunk = f.read(point_struct.size)
                if len(chunk) < point_struct.size:
                    print(f"[WARNING] Stopped early at index {i}, incomplete chunk.")
                    break
                dx, dy, dz, quadrant, magnitude = point_struct.unpack(chunk)
                if any(map(lambda x: not isinstance(x, float) or not x == x, (dx, dy, dz))):
                    print(f"[WARNING] NaN or invalid vector at index {i}, skipping.")
                    continue
                trajectory_points.append((dx, dy, dz, quadrant, magnitude))

    except FileNotFoundError:
        print(f"[ERROR] Trajectory file not found: {traj_bin_file_path}")
        return

    if not trajectory_points:
        print("[ERROR] No trajectory points were loaded.")
        return

    dxs, dys, dzs, quadrants, magnitudes = zip(*trajectory_points)

    # 🧠 Get predicted quadrant string
    print(f"[INFO] Predicted quadrant sequence: {predicted_quads}")

    # Simulate predicted vectors as simplified linear step vectors in red
    if len(trajectory_points) >= 2:
        last_dx, last_dy, last_dz, _, _ = trajectory_points[-1]
        prev_dx, prev_dy, prev_dz, _, _ = trajectory_points[-2]
        step_dx = last_dx - prev_dx
        step_dy = last_dy - prev_dy
        step_dz = last_dz - prev_dz

        red_vectors = []
        base_dx, base_dy, base_dz = last_dx, last_dy, last_dz
        for _ in predicted_quads:
            base_dx += step_dx
            base_dy += step_dy
            base_dz += step_dz
            red_vectors.append((base_dx, base_dy, base_dz))

        rdxs, rdys, rdzs = zip(*red_vectors)

    # 🔷 Plotting
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    try:
        # Original data (blue)
        ax.quiver(
            [0]*len(dxs), [0]*len(dys), [0]*len(dzs),
            dxs, dys, dzs,
            length=1.0, normalize=True, color='blue', linewidth=0.5, alpha=0.7
        )

        # Prediction data (red, slightly beneath for visibility)
        if len(trajectory_points) >= 2:
            ax.quiver(
                [0]*len(rdxs), [0]*len(rdys), [0]*len(rdzs),
                rdxs, rdys, rdzs,
                length=1.0, normalize=True, color='red', linewidth=1.5, alpha=0.6
            )

        ax.set_xlabel('dx - Temperature')
        ax.set_ylabel('dy - Humidity')
        ax.set_zlabel('dz - Pressure')
        ax.set_title("Environmental Trajectory with Prediction Overlay")

        latest_folder = file_handler.get_latest_weather_data_folder(plots_dir)
        save_path = os.path.join(latest_folder, "trajectory.png")
        plt.savefig(save_path)
        print(f"[INFO] Plot saved at {save_path}")

        plt.show()

    except Exception as e:
        print(f"[ERROR] Failed to plot vectors: {e}")

def compute_trajectory_from_bin(dll_path, input_path, output_path):
    try:
        mylib = ctypes.WinDLL(dll_path)
    except Exception as e:
        print(f"Failed to load DLL: {e}")
        return

    if not hasattr(mylib, 'compute_weather_trajectory_bin'):
        print("DLL missing 'compute_weather_trajectory_bin'")
        return

    compute_func = mylib.compute_weather_trajectory_bin
    compute_func.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    compute_func.restype = None

   
    print(f"Loading: {input_path}")
    print(f"Saving: {output_path}")

    compute_func(input_path.encode("utf-8"), output_path.encode("utf-8"))
    print("Trajectory computation complete")

def get_average_trajectory_values(bin_file_path):
    """
    Reads the trajectory_data.bin file generated by compute_weather_trajectory_bin.
    Returns a tuple (avg_dx, avg_dy, avg_dz, avg_magnitude), calculated only from complete rows.

    File format:
       [uint32_t count] [repeating 20-byte records]
       Each record = 3 floats (dx, dy, dz), 1 int (quadrant), 1 float (magnitude)

    NOTE: Only complete, valid records (derived from complete weather data:
          temp, humidity, pressure, and wind) are included in the average.
          If any of dx, dy, dz, or magnitude is NaN or missing, that row is skipped.
    """
    point_struct = struct.Struct('fffif')  # float, float, float, int, float

    if not os.path.exists(bin_file_path):
        print(f"[ERROR] Trajectory file not found: {bin_file_path}")
        return None

    try:
        with open(bin_file_path, 'rb') as f:
            # Read number of points
            header = f.read(4)
            if len(header) < 4:
                print("[ERROR] Not enough data to read point count.")
                return None

            point_count = struct.unpack('I', header)[0]
            if point_count == 0:
                print("[WARNING] No points in trajectory_data.bin.")
                return None

            sum_dx = 0.0
            sum_dy = 0.0
            sum_dz = 0.0
            sum_magnitude = 0.0
            valid_count = 0

            for i in range(point_count):
                chunk = f.read(point_struct.size)
                if len(chunk) < point_struct.size:
                    print(f"[WARNING] Incomplete record at index {i} — skipping.")
                    continue

                dx, dy, dz, quadrant, magnitude = point_struct.unpack(chunk)

                # Skip rows if any value is NaN (dx, dy, dz, magnitude)
                if any(val != val for val in (dx, dy, dz, magnitude)):
                    continue

                # Count only fully valid rows
                sum_dx += dx
                sum_dy += dy
                sum_dz += dz
                sum_magnitude += magnitude
                valid_count += 1

            if valid_count == 0:
                print("[ERROR] No valid rows with complete weather data.")
                return None
            
            return (
                sum_dx / valid_count,
                sum_dy / valid_count,
                sum_dz / valid_count,
                sum_magnitude / valid_count

            )

    except Exception as ex:
        print(f"[ERROR] Failed to read trajectory data: {ex}")
        return None


def open_trajectory(plots_dir, dll_path, input_path, output_path):
    traj_bin_file_path = os.path.join(file_handler.get_latest_weather_data_folder(plots_dir), "trajectory_data.bin")
    load_and_plot_trajectory(plots_dir, traj_bin_file_path, dll_path, input_path, output_path)

    
def get_prediction(plots_dir, dll_path, input_path, output_path, date_str, time_str):
    traj_bin_file_path = os.path.join(file_handler.get_latest_weather_data_folder(plots_dir), "trajectory_data.bin")
    predicted_sequence= get_prediction_traj(dll_path, traj_bin_file_path)
    chart.chart_prediction_run(plots_dir, traj_bin_file_path, predicted_sequence, date_str, time_str)
    display_traj_prediction(plots_dir, predicted_sequence, traj_bin_file_path, dll_path, input_path, output_path)

