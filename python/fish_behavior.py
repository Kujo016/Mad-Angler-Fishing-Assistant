import os 
import ctypes
import struct
import tkinter as tk
from python import file_handler


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

# Define common bite-productive patterns (quadrant labels)
BITE_PATTERNS = [
    ['b'],
    ['f', 'b'],
    ['g', 'b'],
    ['e', 'f', 'b']
]

def ana_bite_pat(plots_dir, dll_path):

    latest_folder = file_handler.get_latest_weather_data_folder(plots_dir)
    traj_bin_file_path = os.path.join(latest_folder, "trajectory_data.bin")
    output_txt_path = os.path.join(latest_folder, "bite_pattern_analysis.txt")

    # Create a new GUI window
    result_window = tk.Toplevel()
    result_window.title("Bite Pattern Analysis")
    result_window.geometry("600x300")

    text_area = tk.Text(result_window, wrap="word", font=("Consolas", 12))
    text_area.pack(padx=10, pady=10, fill="both", expand=True)

    output_lines = []  # Save for writing to file

    if not os.path.exists(traj_bin_file_path):
        error_msg = "Must Generate Trajectory First\n"
        text_area.insert("end", error_msg)
        text_area.tag_add("error", "1.0", "end")
        text_area.tag_config("error", foreground="red", font=("Consolas", 12, "bold"))
        output_lines.append(error_msg)
    else:
        sequence = extract_quadrant_sequence_from_bin(traj_bin_file_path)
        if not sequence:
            error_msg = "Trajectory file is empty or unreadable.\n"
            text_area.insert("end", error_msg)
            text_area.tag_add("error", "1.0", "end")
            text_area.tag_config("error", foreground="red", font=("Consolas", 12, "bold"))
            output_lines.append(error_msg)
        else:
            total_points = len(sequence)
            header = f"Total trajectory points: {total_points}\n\n"
            text_area.insert("end", header)
            output_lines.append(header)

            for pattern in BITE_PATTERNS:
                matches = count_pattern_occurrences(sequence, [ord(p) for p in pattern])
                possible_windows = total_points - len(pattern) + 1
                probability = matches / possible_windows if possible_windows > 0 else 0
                pattern_str = '-'.join(pattern)
                line = f"Pattern: {pattern_str:10} | Matches: {matches:3} / {possible_windows:3} | Probability: {probability:.3f}\n"
                text_area.insert("end", line)
                output_lines.append(line)

            # 🎣 Call DLL to get Fishing Score
            if os.path.exists(dll_path):
                try:
                    mylib = ctypes.WinDLL(dll_path)
                    get_score = mylib.get_fishing_score
                    get_score.argtypes = [ctypes.c_char_p]
                    get_score.restype = ctypes.c_float

                    score = get_score(traj_bin_file_path.encode("utf-8"))
                    score_line = f"\n🎣 Mad Angler Fishing Score: {score:.2f} / 100\n"
                    text_area.insert("end", score_line)
                    output_lines.append(score_line)

                except Exception as e:
                    error_msg = f"[ERROR] Could not compute fishing score: {e}\n"
                    text_area.insert("end", error_msg)
                    output_lines.append(error_msg)
            else:
                warn_msg = "[WARN] OmniBase.dll not found. Skipping fishing score.\n"
                text_area.insert("end", warn_msg)
                output_lines.append(warn_msg)

    # Write output to file
    try:
        with open(output_txt_path, 'w', encoding='utf-8') as f:
            f.writelines(output_lines)
        print(f"[INFO] Bite pattern analysis saved to: {output_txt_path}")
    except Exception as e:
        print(f"[ERROR] Failed to write analysis file: {e}")

# Load quadrant labels from binary trajectory data

def extract_quadrant_sequence_from_bin(bin_path):
    point_struct = struct.Struct('fffif')  # dx, dy, dz, quadrant (int), magnitude
    sequence = []

    with open(bin_path, 'rb') as f:
        count_bytes = f.read(4)
        if len(count_bytes) < 4:
            return []

        point_count = struct.unpack('I', count_bytes)[0]
        for _ in range(point_count):
            chunk = f.read(point_struct.size)
            if len(chunk) < point_struct.size:
                break
            _, _, _, quadrant, _ = point_struct.unpack(chunk)
            sequence.append(quadrant)
    print(sequence)
    for quadrant in sequence:
        print(quadrant)
    return sequence

# Find how often each pattern occurs

def count_pattern_occurrences(sequence, pattern):
    count = 0
    pattern_len = len(pattern)
    for i in range(len(sequence) - pattern_len + 1):
        if sequence[i:i+pattern_len] == pattern:
            count += 1
    return count

# Main analysis function

def analyze_bite_patterns(bin_path):
    sequence = extract_quadrant_sequence_from_bin(bin_path)
    if not sequence:
        print("No trajectory data found.")
        return

    total_points = len(sequence)
    print(f"Total trajectory points: {total_points}")

    results = []

    for pattern in BITE_PATTERNS:
        matches = count_pattern_occurrences(sequence, [ord(p) for p in pattern])
        possible_windows = total_points - len(pattern) + 1
        probability = matches / possible_windows if possible_windows > 0 else 0
        pattern_str = '-'.join(pattern)
        results.append((pattern_str, matches, possible_windows, probability))

    print("\nFishing Pattern Analysis Results:")
    for pattern, matches, windows, prob in results:
        print(f"Pattern: {pattern:10} | Matches: {matches:3} / {windows:3} | Probability: {prob:.3f}")
 