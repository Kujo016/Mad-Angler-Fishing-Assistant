#include "../cpp/trajectory.h"


std::vector<TrajectoryPoint> predict_next_trajectory(const std::vector<TrajectoryPoint>& past_data, int future_steps) {
    std::vector<TrajectoryPoint> forecast;

    if (past_data.size() < 2) return forecast;

    // Simple linear extrapolation (or momentum vector)
    TrajectoryPoint last = past_data.back();
    TrajectoryPoint prev = past_data[past_data.size() - 2];

    float dx = last.dx - prev.dx;
    float dy = last.dy - prev.dy;
    float dz = last.dz - prev.dz;

    for (int i = 1; i <= future_steps; ++i) {
        TrajectoryPoint next;
        next.dx = last.dx + dx * i;
        next.dy = last.dy + dy * i;
        next.dz = last.dz + dz * i;
        
        next.magnitude = std::sqrt(next.dx * next.dx + next.dy * next.dy + next.dz * next.dz);
        next.quadrant = calculate_quadrant(next.dx, next.dy);
        forecast.push_back(next);
    }

    return forecast;
}

// Quadrants for indexing
int quadrant_to_index(char q) {
    if (q < 'a' || q > 'h') return 8; // 'x' or unknown
    return q - 'a';
}

// Extract quadrant sequence from binary
std::vector<char> extract_quadrant_sequence(const std::string& filepath) {
    std::ifstream in(filepath, std::ios::binary);
    std::vector<char> sequence;
    if (!in.is_open()) return sequence;

    uint32_t count;
    in.read(reinterpret_cast<char*>(&count), sizeof(uint32_t));
    for (uint32_t i = 0; i < count; ++i) {
        float dx, dy, dz, magnitude;
        int quadrant;
        in.read(reinterpret_cast<char*>(&dx), sizeof(float));
        in.read(reinterpret_cast<char*>(&dy), sizeof(float));
        in.read(reinterpret_cast<char*>(&dz), sizeof(float));
        in.read(reinterpret_cast<char*>(&quadrant), sizeof(int));
        in.read(reinterpret_cast<char*>(&magnitude), sizeof(float));
        sequence.push_back(static_cast<char>(quadrant));
    }
    return sequence;
}

char calculate_quadrant(float dx, float dy) {
    if (dx > 0 && dy > 0) return 'b';
    if (dx < 0 && dy > 0) return 'c';
    if (dx < 0 && dy < 0) return 'd';
    if (dx > 0 && dy < 0) return 'g';
    return 'x'; // unknown/neutral
}

extern "C" __declspec(dllexport)
void get_predicted_quadrants(const char* traj_path, char* buffer, int buffer_size) {
    std::ifstream fin(traj_path, std::ios::binary);
    if (!fin) return;

    uint32_t count;
    fin.read(reinterpret_cast<char*>(&count), sizeof(count));
    if (count == 0) return;

    std::string sequence;
    for (uint32_t i = 0; i < count; ++i) {
        float dx, dy, dz, magnitude;
        int quadrant;
        fin.read(reinterpret_cast<char*>(&dx), sizeof(float));
        fin.read(reinterpret_cast<char*>(&dy), sizeof(float));
        fin.read(reinterpret_cast<char*>(&dz), sizeof(float));
        fin.read(reinterpret_cast<char*>(&quadrant), sizeof(int));
        fin.read(reinterpret_cast<char*>(&magnitude), sizeof(float));

        if (fin.eof() || fin.fail()) break;

        if (quadrant >= 0 && quadrant < 8) {
            sequence += static_cast<char>('a' + quadrant);
        }

    }

    // Truncate to buffer size
    if (buffer && buffer_size > 0) {
        strncpy(buffer, sequence.c_str(), buffer_size - 1);
        buffer[buffer_size - 1] = '\0';
    }
}



extern "C" __declspec(dllexport) void __stdcall compute_weather_trajectory_bin(const char* input_bin_path, const char* output_bin_path) {
    std::ifstream in(input_bin_path, std::ios::binary);
    if (!in.is_open()) {
        std::cerr << "Failed to open: " << input_bin_path << std::endl;
        return;
    }

    // Read number of records
    uint32_t num_records;
    in.read(reinterpret_cast<char*>(&num_records), sizeof(uint32_t));

    std::vector<WeatherPoint> points(num_records);
    in.read(reinterpret_cast<char*>(points.data()), num_records * sizeof(WeatherPoint));
    in.close();

    std::vector<TrajectoryPoint> trajectory;
    
    compute_weather_trajectory(points, trajectory);

    std::ofstream out(output_bin_path, std::ios::binary);
    if (!out.is_open()) {
        std::cerr << "Failed to open output: " << output_bin_path << std::endl;
        return;
    }

    uint32_t out_count = static_cast<uint32_t>(trajectory.size());
    out.write(reinterpret_cast<const char*>(&out_count), sizeof(uint32_t));
    out.write(reinterpret_cast<const char*>(trajectory.data()), trajectory.size() * sizeof(TrajectoryPoint));
    out.close();

    std::cout << "Trajectory data written to: " << output_bin_path << std::endl;
}
